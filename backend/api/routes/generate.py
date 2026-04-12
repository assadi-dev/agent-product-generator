import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from backend.models.requests import GenerateRequest
from backend.models.responses import GenerateResponse

router = APIRouter()


def _initial_state(request: GenerateRequest) -> dict:
    return {
        "request": request,
        "scraped_content": None,
        "messages": [],
        "product_sheet": None,
        "agent_trace": [],
        "iteration_count": 0,
        "error": None,
    }


@router.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    """Synchronous endpoint — runs the full agent and returns the completed ProductSheet."""
    from backend.agent.graph import build_graph
    graph, thread_id = build_graph()
    config = {"configurable": {"thread_id": thread_id}}

    try:
        final_state = await graph.ainvoke(_initial_state(request), config=config)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    if final_state.get("error") and not final_state.get("product_sheet"):
        raise HTTPException(status_code=422, detail=final_state["error"])

    sheet = final_state.get("product_sheet")
    if sheet is None:
        raise HTTPException(status_code=422, detail="Agent did not produce a product sheet.")

    sheet.agent_trace = final_state.get("agent_trace", [])
    return GenerateResponse(success=True, product_sheet=sheet)


@router.post("/generate/stream")
async def generate_stream(request: GenerateRequest):
    """
    SSE streaming endpoint.
    Uses astream(stream_mode='updates') — more reliable than astream_events across LangGraph versions.
    Event types: tool_start | tool_end | complete | error
    """
    from backend.agent.graph import build_graph
    from langchain_core.messages import AIMessage, ToolMessage

    graph, thread_id = build_graph()
    config = {"configurable": {"thread_id": thread_id}}

    async def event_generator():
        try:
            async for chunk in graph.astream(
                _initial_state(request),
                config=config,
                stream_mode="updates",
            ):
                for node_name, state_update in chunk.items():
                    if node_name == "__end__":
                        continue

                    # Agent node returned — detect tool calls in the new messages
                    if node_name == "agent":
                        for msg in state_update.get("messages", []):
                            if isinstance(msg, AIMessage) and getattr(msg, "tool_calls", None):
                                for tc in msg.tool_calls:
                                    payload = json.dumps({"type": "tool_start", "tool": tc["name"]})
                                    yield f"data: {payload}\n\n"

                    # Tools node returned — detect completed tool calls
                    elif node_name == "tools":
                        for msg in state_update.get("messages", []):
                            if isinstance(msg, ToolMessage) and msg.name:
                                payload = json.dumps({"type": "tool_end", "tool": msg.name})
                                yield f"data: {payload}\n\n"

                    # scrape_url node returned
                    elif node_name == "scrape_url":
                        payload = json.dumps({"type": "tool_end", "tool": "scrape_product_url"})
                        yield f"data: {payload}\n\n"

                    # Any node that produced a product_sheet → generation complete
                    sheet = state_update.get("product_sheet")
                    if sheet is not None:
                        payload = json.dumps({
                            "type": "complete",
                            "sheet": sheet.model_dump(mode="json"),
                        })
                        yield f"data: {payload}\n\n"

                    # Any node that produced an error
                    error = state_update.get("error")
                    if error:
                        payload = json.dumps({"type": "error", "message": error})
                        yield f"data: {payload}\n\n"

        except Exception as exc:
            payload = json.dumps({"type": "error", "message": str(exc)})
            yield f"data: {payload}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
