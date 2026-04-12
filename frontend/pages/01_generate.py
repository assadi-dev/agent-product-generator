"""
Main generation page — two-column layout:
  Left : input form
  Right: live agent trace + product sheet preview + export
"""
import streamlit as st
from frontend.utils.session_state import init_session, save_to_history, set_current_sheet
from frontend.components.input_form import render_input_form
from frontend.components.agent_trace import stream_with_trace
from frontend.components.sheet_preview import render_sheet_preview
from frontend.components.export_panel import render_export_panel

st.set_page_config(page_title="Generate — Product Sheet Generator", layout="wide")
init_session()

st.title("Generate Product Sheet")
st.markdown("Fill in the form and let the AI agent craft a complete product sheet for you.")

left, right = st.columns([1, 2], gap="large")

with left:
    form_data = render_input_form()

with right:
    trace_placeholder = st.empty()
    sheet_placeholder = st.empty()

    if form_data:
        st.session_state.generating = True
        set_current_sheet(None)

        with trace_placeholder.container():
            st.info("Agent starting...")

        sheet = stream_with_trace(form_data, sheet_placeholder, trace_placeholder)

        st.session_state.generating = False

        if sheet:
            # Attach optional image from session state (not sent to the agent)
            sheet["product_image_b64"] = st.session_state.get("product_image_b64")
            set_current_sheet(sheet)
            save_to_history(sheet)
            trace_placeholder.empty()
            with sheet_placeholder.container():
                render_sheet_preview(sheet)
                render_export_panel(sheet)
        else:
            trace_placeholder.error("Generation failed. Check the backend logs.")

    # If a previous sheet exists in session, display it
    elif st.session_state.get("current_sheet"):
        with sheet_placeholder.container():
            render_sheet_preview(st.session_state.current_sheet)
            render_export_panel(st.session_state.current_sheet)
    else:
        with sheet_placeholder.container():
            st.info("Your generated product sheet will appear here.")
