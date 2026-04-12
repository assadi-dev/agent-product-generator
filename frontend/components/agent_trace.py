"""
Live agent trace component — consumes SSE stream from the backend.
"""
import streamlit as st

TOOL_LABELS = {
    "scrape_product_url": "Scraping product URL",
    "generate_product_description": "Generating product description",
    "extract_key_features": "Extracting key features",
    "extract_seo_keywords": "Extracting SEO keywords",
    "adapt_tone": "Adapting tone",
    "localize_content": "Localising content",
    "format_product_sheet": "Assembling final product sheet",
}


def render_agent_trace(trace: list[str]):
    """Renders a static trace list (used after generation completes)."""
    with st.expander("Agent reasoning trace", expanded=False):
        for step in trace:
            st.markdown(f"- {step}")


def stream_with_trace(payload: dict, sheet_placeholder, trace_placeholder) -> dict | None:
    """
    Calls the SSE stream endpoint, updates the trace live, and returns the final sheet dict.
    Returns None on error.
    """
    from frontend.utils.api_client import generate_stream

    active_tools: list[str] = []
    completed_tools: list[str] = []
    sheet = None

    try:
        for event in generate_stream(payload):
            event_type = event.get("type")

            if event_type == "tool_start":
                tool_name = event.get("tool", "")
                if tool_name not in active_tools:
                    active_tools.append(tool_name)
                _update_trace_ui(trace_placeholder, active_tools, completed_tools)

            elif event_type == "tool_end":
                tool_name = event.get("tool", "")
                if tool_name in active_tools:
                    active_tools.remove(tool_name)
                if tool_name not in completed_tools:
                    completed_tools.append(tool_name)
                _update_trace_ui(trace_placeholder, active_tools, completed_tools)

            elif event_type == "complete":
                sheet = event.get("sheet")
                # Mark any remaining active tools as done
                for t in list(active_tools):
                    completed_tools.append(t)
                active_tools.clear()
                _update_trace_ui(trace_placeholder, active_tools, completed_tools)

            elif event_type == "error":
                trace_placeholder.error(f"Agent error: {event.get('message', 'Unknown error')}")
                return None

    except Exception as exc:
        trace_placeholder.error(f"Connection error: {exc}")
        return None

    if sheet is None:
        trace_placeholder.error("Generation completed but no product sheet was returned.")
    return sheet


def _update_trace_ui(placeholder, active: list[str], completed: list[str]):
    with placeholder.container():
        st.markdown("**Agent Progress**")
        for tool in completed:
            label = TOOL_LABELS.get(tool, tool)
            st.markdown(f"✅ {label}")
        for tool in active:
            label = TOOL_LABELS.get(tool, tool)
            st.markdown(f"⏳ {label}...")
