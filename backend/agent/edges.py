"""
Conditional edge functions for the LangGraph state graph.
Each function returns a string key that maps to the next node.
"""
from langchain_core.messages import AIMessage
from backend.agent.state import AgentState


def should_scrape(state: AgentState) -> str:
    """After route_input: scrape if a URL was provided."""
    if state["request"].source_url:
        return "scrape_url"
    return "agent"


def should_continue(state: AgentState) -> str:
    """After agent_node: route to tools, validate, or error."""
    if state.get("error"):
        return "error"

    messages = state.get("messages", [])
    if not messages:
        return "error"

    last_msg = messages[-1]
    # If the LLM issued tool calls, run them
    if isinstance(last_msg, AIMessage) and getattr(last_msg, "tool_calls", None):
        return "tools"

    # No more tool calls — try to validate the output
    return "validate"


def is_valid(state: AgentState) -> str:
    """After validate_output: done or retry."""
    if state.get("product_sheet") is not None:
        return "done"
    if state.get("iteration_count", 0) >= 5:
        return "done"  # Give up — surface partial error to caller
    return "retry"
