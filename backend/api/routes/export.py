import json
import time
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from backend.models.product_sheet import ProductSheet

router = APIRouter()


@router.post("/export/json")
async def export_json(sheet: ProductSheet):
    """Returns the ProductSheet as a formatted, downloadable JSON file. Image is excluded."""
    content = json.dumps(
        sheet.model_dump(mode="json", exclude={"product_image_b64"}),
        indent=2,
        ensure_ascii=False,
    )
    filename = f"{int(time.time())}.json"
    return Response(
        content=content.encode("utf-8"),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/export/pdf")
async def export_pdf(sheet: ProductSheet):
    """Generates and returns a styled PDF product sheet using ReportLab."""
    from backend.services.export_service import generate_pdf
    try:
        pdf_bytes = generate_pdf(sheet)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {exc}")

    filename = f"{int(time.time())}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
