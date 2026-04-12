import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from backend.models.product_sheet import ProductSheet

router = APIRouter()


@router.post("/export/json")
async def export_json(sheet: ProductSheet):
    """Returns the ProductSheet as a formatted, downloadable JSON file."""
    content = json.dumps(sheet.model_dump(mode="json"), indent=2, ensure_ascii=False)
    filename = sheet.product_name.lower().replace(" ", "_") + "_sheet.json"
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

    filename = sheet.product_name.lower().replace(" ", "_") + "_sheet.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
