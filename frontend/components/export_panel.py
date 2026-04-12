"""
Export buttons for downloading the product sheet as PDF or JSON.
Filenames use Unix timestamp format: {timestamp}.{ext}
Image is included in PDF but excluded from JSON.
"""
import json
import time
import streamlit as st


def render_export_panel(sheet: dict):
    """Renders PDF and JSON download buttons for a completed product sheet."""
    from frontend.utils.api_client import export_pdf

    st.markdown("### Export")
    col1, col2 = st.columns(2)

    with col1:
        try:
            # Send the full sheet (including product_image_b64 if present) to PDF endpoint
            pdf_bytes = export_pdf(sheet)
            st.download_button(
                label="Download PDF",
                data=pdf_bytes,
                file_name=f"{int(time.time())}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as exc:
            st.error(f"PDF export failed: {exc}")

    with col2:
        # Exclude image from JSON export
        sheet_for_json = {k: v for k, v in sheet.items() if k != "product_image_b64"}
        json_str = json.dumps(sheet_for_json, indent=2, ensure_ascii=False, default=str)
        st.download_button(
            label="Download JSON",
            data=json_str.encode("utf-8"),
            file_name=f"{int(time.time())}.json",
            mime="application/json",
            use_container_width=True,
        )
