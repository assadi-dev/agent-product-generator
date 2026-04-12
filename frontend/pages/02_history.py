"""
History page — shows the last 20 generated product sheets from session state.
"""
import streamlit as st
from frontend.utils.session_state import init_session, get_history, set_current_sheet
from frontend.components.sheet_preview import render_sheet_preview
from frontend.components.export_panel import render_export_panel

st.set_page_config(page_title="History — Product Sheet Generator", layout="wide")
init_session()

st.title("Generation History")
st.markdown("Your last 20 generated product sheets (stored in this session).")

history = get_history()

if not history:
    st.info("No product sheets generated yet. Go to the **Generate** page to create one.")
else:
    for i, sheet in enumerate(history):
        with st.expander(
            f"{sheet.get('product_name', 'Unknown')} — {sheet.get('category', '')} "
            f"({sheet.get('tone', '')} · {sheet.get('language', '')})",
            expanded=(i == 0),
        ):
            col1, col2 = st.columns([3, 1])
            with col1:
                render_sheet_preview(sheet)
            with col2:
                render_export_panel(sheet)
                if st.button("Load in Generator", key=f"load_{i}"):
                    set_current_sheet(sheet)
                    st.switch_page("pages/01_generate.py")
