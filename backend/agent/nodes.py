"""
LangGraph node functions for the product sheet agent.
Each function takes AgentState and returns a partial state update dict.
"""
import json
from langchain_core.messages import SystemMessage, AIMessage
from backend.agent.state import AgentState
from backend.models.product_sheet import ProductSheet
from backend.config import settings


# ---------------------------------------------------------------------------
# System prompt builder
# ---------------------------------------------------------------------------

def _build_system_prompt(state: AgentState) -> str:
    req = state["request"]
    context_hint = ""
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
# route_input node — decides whether to scrape a URL first
# ---------------------------------------------------------------------------

async def route_input_node(state: AgentState) -> dict:
    """
    Initialises the state. Web scraping is handled as a separate node (scrape_url_node)
    before this hands off to the main agent loop.
    """
    return {
        "scraped_content": state.get("scraped_content"),
        "agent_trace": ["Starting product sheet generation..."],
        "iteration_count": 0,
        "error": None,
        "product_sheet": None,
        "messages": [],
    }


# ---------------------------------------------------------------------------
# scrape_url node — fetches and stores scraped content in state
# ---------------------------------------------------------------------------

async def scrape_url_node(state: AgentState) -> dict:
    from backend.agent.tools.web_scraper import scrape_product_url
    url = state["request"].source_url
    trace = state.get("agent_trace", [])
    try:
        result = await scrape_product_url.ainvoke({"url": url})
        trace = trace + [f"Scraped URL: {url}"]
        return {"scraped_content": result, "agent_trace": trace}
    except Exception as exc:
        trace = trace + [f"URL scraping failed: {exc}"]
        return {"scraped_content": None, "agent_trace": trace}


# ---------------------------------------------------------------------------
# agent node — the core ReAct LLM node
# ---------------------------------------------------------------------------

async def agent_node(state: AgentState, llm_with_tools) -> dict:
    """Core ReAct reasoning node. LLM receives full context and decides which tools to call."""
    iteration = state.get("iteration_count", 0)
    if iteration >= settings.agent_max_iterations:
        return {"error": f"Agent exceeded {settings.agent_max_iterations} iterations without completing."}

    system_msg = SystemMessage(content=_build_system_prompt(state))

    # Build context message if we have scraped content and no messages yet
    initial_messages = list(state.get("messages", []))
    if not initial_messages and state.get("scraped_content"):
        from langchain_core.messages import HumanMessage
        initial_messages = [
            HumanMessage(content=f"Scraped product page content:\n\n{state['scraped_content']}\n\nPlease generate the product sheet now.")
        ]
    elif not initial_messages:
        from langchain_core.messages import HumanMessage
        req = state["request"]
        context = req.raw_description or f"No additional context. Use your knowledge of {req.product_name} in the {req.category} category."
        initial_messages = [
            HumanMessage(content=f"Context:\n{context}\n\nPlease generate the product sheet now.")
        ]

    response = await llm_with_tools.ainvoke([system_msg] + initial_messages)

    trace = state.get("agent_trace", [])
    # Extract tool calls for trace
    if hasattr(response, "tool_calls") and response.tool_calls:
        for tc in response.tool_calls:
            trace = trace + [f"Calling tool: {tc['name']}"]

    return {
        "messages": initial_messages + [response],
        "iteration_count": iteration + 1,
        "agent_trace": trace,
    }


# ---------------------------------------------------------------------------
# validate_output node — attempts to parse the final product sheet from messages
# ---------------------------------------------------------------------------

def validate_output_node(state: AgentState) -> dict:
    """
    Searches recent tool messages for a valid ProductSheet JSON.
    Sets state['product_sheet'] if found, otherwise sets state['error'].
    """
    from langchain_core.messages import ToolMessage
    messages = state.get("messages", [])

    # Look for format_product_sheet tool result
    for msg in reversed(messages):
        if isinstance(msg, ToolMessage) and msg.name == "format_product_sheet":
            try:
                sheet = ProductSheet.model_validate_json(msg.content)
                sheet.agent_trace = state.get("agent_trace", [])
                return {
                    "product_sheet": sheet,
                    "agent_trace": state.get("agent_trace", []) + ["Product sheet validated successfully."],
                }
            except Exception as exc:
                return {"error": f"ProductSheet validation failed: {exc}"}

    return {"error": "format_product_sheet was never called. Cannot finalise product sheet."}


# ---------------------------------------------------------------------------
# error node
# ---------------------------------------------------------------------------

def error_node(state: AgentState) -> dict:
    return {
        "agent_trace": state.get("agent_trace", []) + [f"Error: {state.get('error', 'Unknown error')}"],
    }
