"""
Renders a product sheet dict as a styled Streamlit preview.
"""
import streamlit as st


def render_sheet_preview(sheet: dict):
    """Renders the full product sheet with all sections."""
    st.divider()

    # Hero
    st.markdown(f"## {sheet.get('title', sheet.get('product_name', ''))}")
    st.markdown(f"*{sheet.get('tagline', '')}*")
    st.divider()

    # Descriptions
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("**Quick Pitch**")
        st.info(sheet.get("short_description", ""))
    with col2:
        st.markdown("**Full Description**")
        st.markdown(sheet.get("full_description", ""))

    st.divider()

    # Features
    st.markdown("### Key Features")
    features = sheet.get("key_features", [])
    cols = st.columns(2)
    for i, feature in enumerate(features):
        with cols[i % 2]:
            st.markdown(f"✓ {feature}")

    # Technical specs
    specs = sheet.get("technical_specs", [])
    if specs:
        st.divider()
        st.markdown("### Technical Specifications")
        spec_data = {s["label"]: s["value"] for s in specs}
        for label, value in spec_data.items():
            col_a, col_b = st.columns([1, 2])
            col_a.markdown(f"**{label}**")
            col_b.markdown(value)

    st.divider()

    # SEO section
    with st.expander("SEO Assets", expanded=True):
        st.markdown(f"**Meta Title** *(max 60 chars — current: {len(sheet.get('meta_title', ''))})*")
        st.code(sheet.get("meta_title", ""), language=None)

        st.markdown(f"**Meta Description** *(max 155 chars — current: {len(sheet.get('meta_description', ''))})*")
        st.code(sheet.get("meta_description", ""), language=None)

        st.markdown("**SEO Keywords**")
        keywords = sheet.get("seo_keywords", [])
        st.markdown(" ".join(f"`{kw}`" for kw in keywords))

    # Target audience
    with st.expander("Target Audience"):
        st.markdown(sheet.get("target_audience", ""))

    # Agent trace
    trace = sheet.get("agent_trace", [])
    if trace:
        with st.expander("Agent Reasoning Trace"):
            for step in trace:
                st.markdown(f"- {step}")

    # Metadata
    st.caption(
        f"Generated at {sheet.get('generated_at', '')} · "
        f"Tone: {sheet.get('tone', '')} · Language: {sheet.get('language', '')}"
    )
