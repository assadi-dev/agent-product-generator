"""
Streamlit entry point.
Run with: streamlit run frontend/app.py
"""
import streamlit as st

st.set_page_config(
    page_title="Product Sheet Generator",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar navigation handled by Streamlit multipage (pages/ directory)
st.sidebar.title("Product Sheet Generator")
st.sidebar.markdown("AI-powered fiche produit generator using a LangGraph agent.")
st.sidebar.divider()

# Show backend status
try:
    from frontend.utils.api_client import health_check
    health = health_check()
    st.sidebar.success(f"Backend online — {health['model']}")
except Exception:
    st.sidebar.warning("Backend offline. Start with: `uvicorn backend.main:app --reload`")

st.sidebar.divider()
st.sidebar.markdown("**Pages**")
st.sidebar.page_link("pages/01_generate.py", label="Generate", icon="✨")
st.sidebar.page_link("pages/02_history.py", label="History", icon="📋")
st.sidebar.page_link("pages/03_about.py", label="About & Architecture", icon="📐")

# Default landing
st.title("Welcome to Product Sheet Generator")
st.markdown(
    """
    An AI agent that creates **complete, publication-ready product sheets** for marketing and e-commerce teams.

    **Powered by:**
    - LangGraph ReAct agent with 7 specialised tools
    - Claude Sonnet (Anthropic) as the reasoning engine
    - FastAPI backend + Streamlit frontend

    Navigate to **Generate** to create your first product sheet.
    """
)
