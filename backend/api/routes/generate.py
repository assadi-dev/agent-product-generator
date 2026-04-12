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

    # Attach trace
    sheet.agent_trace = final_state.get("agent_trace", [])
    return GenerateResponse(success=True, product_sheet=sheet)


@router.post("/generate/stream")
async def generate_stream(request: GenerateRequest):
    """
    SSE streaming endpoint — pushes agent events in real time.
    Event types: tool_start | tool_end | complete | error
    """
    from backend.agent.graph import build_graph
    graph, thread_id = build_graph()
    config = {"configurable": {"thread_id": thread_id}}

    async def event_generator():
        try:
            async for event in graph.astream_events(
                _initial_state(request),
                config=config,
                version="v2",
            ):
                event_type = event.get("event", "")
                name = event.get("name", "")

                if event_type == "on_tool_start":
                    payload = json.dumps({"type": "tool_start", "tool": name})
                    yield f"data: {payload}\n\n"

                elif event_type == "on_tool_end":
                    payload = json.dumps({"type": "tool_end", "tool": name})
                    yield f"data: {payload}\n\n"

                elif event_type == "on_chain_end" and name == "LangGraph":
                    output = event.get("data", {}).get("output", {})
                    sheet = output.get("product_sheet")
                    if sheet is not None:
                        # sheet is a ProductSheet instance
                        payload = json.dumps({"type": "complete", "sheet": sheet.model_dump(mode="json")})
                        yield f"data: {payload}\n\n"

        except Exception as exc:
            payload = json.dumps({"type": "error", "message": str(exc)})
            yield f"data: {payload}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
