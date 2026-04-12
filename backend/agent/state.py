from typing import TypedDict, Annotated, Optional
from langgraph.graph.message import add_messages
from backend.models.requests import GenerateRequest
from backend.models.product_sheet import ProductSheet


class AgentState(TypedDict):
    # User request
    request: GenerateRequest

    # Optional scraped content from URL
    scraped_content: Optional[str]

    # ReAct message list (append-only via add_messages reducer)
    messages: Annotated[list, add_messages]

    # Final assembled product sheet
    product_sheet: Optional[ProductSheet]

    # Human-readable trace of agent steps
    agent_trace: list[str]

    # Guard against infinite loops
    iteration_count: int

    # Error message if something went wrong
    error: Optional[str]
