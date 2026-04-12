"""
Left-panel input form component.
Returns a GenerateRequest-compatible dict when submitted.
"""
import base64
import streamlit as st


def render_input_form() -> dict | None:
    """
    Renders the product generation form.
    Returns the form data dict on submit, or None if not submitted.
    """
    # File uploader must live outside st.form to work correctly in Streamlit
    st.markdown("**Image produit (optionnel)**")
    uploaded = st.file_uploader(
        "Importer une image",
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed",
    )
    if uploaded is not None:
        img_bytes = uploaded.read()
        b64 = base64.b64encode(img_bytes).decode()
        st.session_state["product_image_b64"] = b64
        st.session_state["product_image_mime"] = uploaded.type
        # Use data URI to bypass Streamlit's PIL validation (supports WebP natively in browser)
        st.markdown(
            f'<img src="data:{uploaded.type};base64,{b64}" style="max-width:100%;width:600px;" />',
            unsafe_allow_html=True,
        )
    elif "product_image_b64" not in st.session_state:
        st.session_state["product_image_b64"] = None
        st.session_state["product_image_mime"] = None

    st.divider()

    with st.form("generate_form"):
        st.subheader("Product Details")

        product_name = st.text_input(
            "Product Name *",
            placeholder="e.g. Sony WH-1000XM5",
            help="The name of the product to generate a sheet for.",
        )
        category = st.text_input(
            "Category *",
            placeholder="e.g. Wireless Headphones",
        )
        source_url = st.text_input(
            "Product URL (optional)",
            placeholder="https://example.com/product-page",
            help="The agent will scrape this page for additional context.",
        )
        raw_description = st.text_area(
            "Existing Description (optional)",
            placeholder="Paste any existing product description or notes here...",
            height=100,
        )
        target_audience = st.text_input(
            "Target Audience *",
            placeholder="e.g. Remote workers and frequent travellers aged 25-45",
        )

        st.subheader("Style & Language")
        col1, col2 = st.columns(2)
        with col1:
            tone = st.radio(
                "Tone",
                options=["professional", "casual", "luxury", "technical"],
                index=0,
                horizontal=False,
            )
        with col2:
            language = st.selectbox("Language", options=["en", "fr"], index=0)

        additional_context = st.text_area(
            "Additional Notes (optional)",
            placeholder="Any specific angles, claims, or instructions...",
            height=70,
        )

        submitted = st.form_submit_button("Generate Product Sheet", type="primary", use_container_width=True)

    if submitted:
        if not product_name.strip() or not category.strip() or not target_audience.strip():
            st.error("Product Name, Category, and Target Audience are required.")
            return None
        return {
            "product_name": product_name.strip(),
            "category": category.strip(),
            "source_url": source_url.strip() or None,
            "raw_description": raw_description.strip() or None,
            "target_audience": target_audience.strip(),
            "tone": tone,
            "language": language,
            "additional_context": additional_context.strip() or None,
        }
    return None
