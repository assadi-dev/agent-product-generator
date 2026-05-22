"""
About page — shows project description and the live LangGraph Mermaid diagram.
"""
import streamlit as st

st.set_page_config(page_title="About — Product Sheet Generator", layout="wide")

st.title("About & Architecture")

st.markdown(
    """
## What is this?

An **AI agent** built with [LangGraph](https://github.com/langchain-ai/langgraph) that generates
complete product sheets for marketing and e-commerce teams.

Unlike a simple LLM chain, this agent:
- **Makes decisions**: skips unnecessary tools (e.g. no scraping if no URL provided)
- **Iterates**: validates its own output and retries if the product sheet is incomplete
- **Uses specialised tools**: each tool is a focused LLM call optimised for one task

## Agent Tools

| Tool | Purpose |
|------|---------|
| `scrape_product_url` | Fetch and clean product page content |
| `generate_product_description` | Write title, tagline, short & full description |
| `extract_key_features` | Identify 5-8 concrete USPs |
| `extract_seo_keywords` | Generate keywords, meta title, meta description |
| `adapt_tone` | Rewrite copy in professional / casual / luxury / technical voice |
| `localize_content` | Translate + culturally adapt to French |
| `format_product_sheet` | Validate and assemble the final ProductSheet |

## Tech Stack

- **LangGraph** — stateful agent graph with ReAct loop
- **LangChain Anthropic** — Claude Sonnet as the reasoning engine
- **FastAPI** — REST + SSE streaming backend
- **Streamlit** — real-time frontend with live agent trace
- **ReportLab** — PDF export
- **Pydantic v2** — strict data validation at every layer
"""
)

st.divider()
st.subheader("Live Agent State Graph")
st.markdown("The diagram below is generated directly from the LangGraph compiled graph.")

try:
    from backend.agent.graph import get_graph_mermaid
    mermaid_code = get_graph_mermaid()
    # Render via streamlit-extras mermaid or fallback to code block
    try:
        from streamlit_extras.add_vertical_space import add_vertical_space
        st.markdown(f"```mermaid\n{mermaid_code}\n```")
    except ImportError:
        st.code(mermaid_code, language="text")
    st.caption("Tip: copy the Mermaid code into https://mermaid.live to view the interactive graph.")
except Exception as exc:
    st.warning(f"Could not render graph: {exc}")
    st.markdown(
        """
```mermaid
stateDiagram-v2
    [*] --> route_input
    route_input --> scrape_url : has URL
    route_input --> agent : no URL
    scrape_url --> agent
    agent --> tools : tool_calls
    agent --> validate_output : no tool_calls
    tools --> agent
    validate_output --> [*] : valid
    validate_output --> agent : retry
    agent --> error : max iterations
    error --> [*]
```
        """
    )

st.divider()
st.markdown(
    "Built as a portfolio project to demonstrate practical GenAI agent development. "
    "[Source code available on GitHub](https://github.com/assadi-dev/agent-product-generator)"
)
