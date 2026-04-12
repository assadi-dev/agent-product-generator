"""
Centralised Streamlit session_state helpers.
"""
import streamlit as st
from typing import Optional


def init_session():
    """Initialise session state keys if they don't exist."""
    defaults = {
        "history": [],          # list of ProductSheet dicts
        "current_sheet": None,  # currently displayed sheet dict
        "generating": False,
        "agent_trace": [],
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def save_to_history(sheet: dict):
    st.session_state.history.insert(0, sheet)
    # Keep last 20 sheets in memory
    st.session_state.history = st.session_state.history[:20]


def get_history() -> list[dict]:
    return st.session_state.get("history", [])


def set_current_sheet(sheet: Optional[dict]):
    st.session_state.current_sheet = sheet


def get_current_sheet() -> Optional[dict]:
    return st.session_state.get("current_sheet")
