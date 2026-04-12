"""
LangGraph state graph for the product sheet agent.
Exposes build_graph() which returns a compiled graph ready for ainvoke / astream_events.
"""
from uuid import uuid4
from functools import partial

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from backend.agent.state import AgentState
from backend.agent.nodes import (
    route_input_node,
    scrape_url_node,
    agent_node,
    validate_output_node,
    error_node,
)
from backend.agent.edges import should_scrape, should_continue, is_valid
from backend.agent.tools import ALL_TOOLS
from backend.services.llm_factory import get_llm


def build_graph():
    """
    Builds and compiles the LangGraph state graph.
    Returns a (graph, thread_id) tuple so the caller can pass thread_id in config.
    """
    llm = get_llm()
    llm_with_tools = llm.bind_tools(ALL_TOOLS)

    graph = StateGraph(AgentState)

    # Nodes
    graph.add_node("route_input", route_input_node)
    graph.add_node("scrape_url", scrape_url_node)
    graph.add_node("agent", partial(agent_node, llm_with_tools=llm_with_tools))
    graph.add_node("tools", ToolNode(ALL_TOOLS))
    graph.add_node("validate_output", validate_output_node)
    graph.add_node("error", error_node)

    # Entry point
    graph.set_entry_point("route_input")

    # Edges
    graph.add_conditional_edges(
        "route_input",
        should_scrape,
        {"scrape_url": "scrape_url", "agent": "agent"},
    )
    graph.add_edge("scrape_url", "agent")
    graph.add_conditional_edges(
        "agent",
        should_continue,
        {"tools": "tools", "validate": "validate_output", "error": "error"},
    )
    graph.add_edge("tools", "agent")
    graph.add_conditional_edges(
        "validate_output",
        is_valid,
        {"done": END, "retry": "agent"},
    )
    graph.add_edge("error", END)

    checkpointer = MemorySaver()
    compiled = graph.compile(checkpointer=checkpointer)
    thread_id = str(uuid4())
    return compiled, thread_id


def get_graph_mermaid() -> str:
    """Returns a Mermaid diagram of the graph for the About page."""
    compiled, _ = build_graph()
    return compiled.get_graph().draw_mermaid()
