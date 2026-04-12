"""
Export buttons for downloading the product sheet as PDF or JSON.
"""
import streamlit as st


def render_export_panel(sheet: dict):
    """Renders PDF and JSON download buttons for a completed product sheet."""
    from frontend.utils.api_client import export_pdf, export_json

    st.markdown("### Export")
    col1, col2 = st.columns(2)

    with col1:
        try:
            pdf_bytes = export_pdf(sheet)
            filename = sheet.get("product_name", "product").lower().replace(" ", "_") + "_sheet.pdf"
            st.download_button(
                label="Download PDF",
                data=pdf_bytes,
                file_name=filename,
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as exc:
            st.error(f"PDF export failed: {exc}")

    with col2:
        import json
        json_str = json.dumps(sheet, indent=2, ensure_ascii=False, default=str)
        filename = sheet.get("product_name", "product").lower().replace(" ", "_") + "_sheet.json"
        st.download_button(
            label="Download JSON",
            data=json_str.encode("utf-8"),
            file_name=filename,
            mime="application/json",
            use_container_width=True,
        )
