"""
LangGraph node functions for the product sheet agent.
"""
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from backend.agent.state import AgentState
from backend.models.product_sheet import ProductSheet
from backend.config import settings
from backend.logging_config import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# System prompt builder
# ---------------------------------------------------------------------------

def _build_system_prompt(state: AgentState) -> str:
    req = state["request"]
    if state.get("scraped_content"):
        context_hint = "Scraped web content is available in the conversation — use it as product context."
    elif req.raw_description:
        context_hint = "The user provided a raw product description — use it as the primary context."
    else:
        context_hint = "No external context was provided — rely on your knowledge of this product category."

    return f"""You are a professional product copywriter and SEO specialist working for a marketing agency.

Your task: Generate a complete, publication-ready product sheet for the following product.

Product: {req.product_name}
Category: {req.category}
Target audience: {req.target_audience}
Desired tone: {req.tone.value}
Language: {req.language.value}
{f"Additional context: {req.additional_context}" if req.additional_context else ""}

{context_hint}

MANDATORY TOOL EXECUTION ORDER — follow this sequence:
1. Call `generate_product_description` with all available context.
2. Call `extract_key_features` using the full_description from step 1.
3. Call `extract_seo_keywords` using the description from step 1.
4. Call `adapt_tone` to rewrite the copy in the requested tone.
5. If language is 'fr', call `localize_content` to translate everything.
6. ALWAYS finish by calling `format_product_sheet` to produce the final output.

You may skip `scrape_product_url` if no URL is present.
You may skip `localize_content` if language is 'en'.
Never skip `format_product_sheet` — it is required to complete the task.

Be thorough. Produce rich, detailed content at each step."""


# ---------------------------------------------------------------------------
# route_input node
# ---------------------------------------------------------------------------

async def route_input_node(state: AgentState) -> dict:
    req = state["request"]
    logger.info(
        "agent_start",
        product=req.product_name,
        category=req.category,
        language=req.language.value,
        tone=req.tone.value,
        has_url=bool(req.source_url),
    )
    return {
        "scraped_content": state.get("scraped_content"),
        "agent_trace": ["Starting product sheet generation..."],
        "iteration_count": 0,
        "error": None,
        "product_sheet": None,
        "messages": [],
    }


# ---------------------------------------------------------------------------
# scrape_url node
# ---------------------------------------------------------------------------

async def scrape_url_node(state: AgentState) -> dict:
    from backend.agent.tools.web_scraper import scrape_product_url
    url = state["request"].source_url
    trace = state.get("agent_trace", [])
    try:
        result = await scrape_product_url.ainvoke({"url": url})
        return {"scraped_content": result, "agent_trace": trace + [f"Scraped URL: {url}"]}
    except Exception as exc:
        return {"scraped_content": None, "agent_trace": trace + [f"URL scraping failed: {exc}"]}


# ---------------------------------------------------------------------------
# agent node  — FIXED: returns only NEW messages (add_messages handles accumulation)
# ---------------------------------------------------------------------------

async def agent_node(state: AgentState, llm_with_tools) -> dict:
    """Core ReAct reasoning node."""
    iteration = state.get("iteration_count", 0)
    if iteration >= settings.agent_max_iterations:
        logger.error(
            "agent_max_iterations_exceeded",
            product=state["request"].product_name,
            max_iterations=settings.agent_max_iterations,
        )
        return {"error": f"Agent exceeded {settings.agent_max_iterations} iterations without completing."}

    system_msg = SystemMessage(content=_build_system_prompt(state))
    messages = list(state.get("messages", []))

    # First call only: inject the initial human message into the messages list
    # (it is NOT yet in state — we add it via the return dict so add_messages records it)
    new_messages: list = []
    if not messages:
        if state.get("scraped_content"):
            first_msg = HumanMessage(
                content=f"Scraped product page content:\n\n{state['scraped_content']}\n\nPlease generate the product sheet now."
            )
        else:
            req = state["request"]
            context = req.raw_description or f"Use your knowledge of {req.product_name} in the {req.category} category."
            first_msg = HumanMessage(content=f"Context:\n{context}\n\nPlease generate the product sheet now.")
        messages = [first_msg]
        new_messages.append(first_msg)

    response = await llm_with_tools.ainvoke([system_msg] + messages)
    new_messages.append(response)

    trace = state.get("agent_trace", [])
    if hasattr(response, "tool_calls") and response.tool_calls:
        for tc in response.tool_calls:
            logger.info("tool_call", tool=tc["name"], iteration=iteration)
            trace = trace + [f"Calling tool: {tc['name']}"]
    else:
        logger.info("agent_iteration_no_tools", iteration=iteration)

    return {
        "messages": new_messages,       # ← only NEW messages; add_messages appends them
        "iteration_count": iteration + 1,
        "agent_trace": trace,
    }


# ---------------------------------------------------------------------------
# validate_output node
# ---------------------------------------------------------------------------

def validate_output_node(state: AgentState) -> dict:
    from langchain_core.messages import ToolMessage
    messages = state.get("messages", [])

    for msg in reversed(messages):
        if isinstance(msg, ToolMessage) and msg.name == "format_product_sheet":
            try:
                sheet = ProductSheet.model_validate_json(msg.content)
                sheet.agent_trace = state.get("agent_trace", [])
                logger.info("product_sheet_validated", product=state["request"].product_name)
                return {
                    "product_sheet": sheet,
                    "agent_trace": state.get("agent_trace", []) + ["Product sheet validated successfully."],
                }
            except Exception as exc:
                logger.error("product_sheet_validation_failed", error=str(exc), exc_info=True)
                return {"error": f"ProductSheet validation failed: {exc}"}

    logger.error("format_product_sheet_not_called", product=state["request"].product_name)
    return {"error": "format_product_sheet was never called. Cannot finalise product sheet."}


# ---------------------------------------------------------------------------
# error node
# ---------------------------------------------------------------------------

def error_node(state: AgentState) -> dict:
    return {
        "agent_trace": state.get("agent_trace", []) + [f"Error: {state.get('error', 'Unknown error')}"],
    }
