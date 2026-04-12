"""
PDF export using ReportLab Platypus for clean, paginated output.
"""
from io import BytesIO
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)
from reportlab.platypus import KeepTogether

from backend.models.product_sheet import ProductSheet

# Brand colours
DARK = colors.HexColor("#1A1A2E")
ACCENT = colors.HexColor("#4F46E5")
LIGHT_BG = colors.HexColor("#F8F8FF")
KEYWORD_BG = colors.HexColor("#EEF2FF")
WHITE = colors.white


def _styles():
    base = getSampleStyleSheet()
    return {
        "hero_title": ParagraphStyle(
            "hero_title",
            parent=base["Title"],
            fontSize=26,
            textColor=DARK,
            spaceAfter=4 * mm,
            leading=30,
        ),
        "tagline": ParagraphStyle(
            "tagline",
            parent=base["Normal"],
            fontSize=13,
            textColor=ACCENT,
            spaceAfter=6 * mm,
            fontName="Helvetica-Oblique",
        ),
        "section_heading": ParagraphStyle(
            "section_heading",
            parent=base["Heading2"],
            fontSize=13,
            textColor=DARK,
            fontName="Helvetica-Bold",
            spaceBefore=6 * mm,
            spaceAfter=3 * mm,
        ),
        "body": ParagraphStyle(
            "body",
            parent=base["Normal"],
            fontSize=10,
            textColor=colors.HexColor("#333333"),
            leading=15,
            spaceAfter=3 * mm,
        ),
        "feature": ParagraphStyle(
            "feature",
            parent=base["Normal"],
            fontSize=10,
            textColor=colors.HexColor("#333333"),
            leading=14,
            leftIndent=5 * mm,
        ),
        "meta_label": ParagraphStyle(
            "meta_label",
            parent=base["Normal"],
            fontSize=9,
            fontName="Helvetica-Bold",
            textColor=ACCENT,
        ),
        "meta_value": ParagraphStyle(
            "meta_value",
            parent=base["Normal"],
            fontSize=9,
            textColor=colors.HexColor("#555555"),
            spaceAfter=2 * mm,
        ),
        "footer": ParagraphStyle(
            "footer",
            parent=base["Normal"],
            fontSize=8,
            textColor=colors.HexColor("#999999"),
            alignment=TA_CENTER,
        ),
        "keyword": ParagraphStyle(
            "keyword",
            parent=base["Normal"],
            fontSize=9,
            textColor=ACCENT,
            fontName="Helvetica-Bold",
        ),
    }


def generate_pdf(sheet: ProductSheet) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )
    s = _styles()
    story = []

    # ── Header bar (simulated with a table)
    header_table = Table(
        [[Paragraph("PRODUCT SHEET", ParagraphStyle("h", fontSize=8, textColor=WHITE, fontName="Helvetica-Bold"))]],
        colWidths=[doc.width],
        rowHeights=[8 * mm],
    )
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), ACCENT),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5 * mm),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 5 * mm))

    # ── Hero
    story.append(Paragraph(sheet.title, s["hero_title"]))
    story.append(Paragraph(sheet.tagline, s["tagline"]))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=4 * mm))

    # ── Short description
    story.append(Paragraph("Overview", s["section_heading"]))
    story.append(Paragraph(sheet.short_description, s["body"]))

    # ── Full description
    story.append(Paragraph("Product Description", s["section_heading"]))
    for para in sheet.full_description.split("\n\n"):
        if para.strip():
            story.append(Paragraph(para.strip(), s["body"]))

    # ── Key features
    story.append(Paragraph("Key Features", s["section_heading"]))
    feature_rows = [[Paragraph(f"✓  {feat}", s["feature"])] for feat in sheet.key_features]
    if feature_rows:
        feat_table = Table(feature_rows, colWidths=[doc.width])
        feat_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BG),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [WHITE, LIGHT_BG]),
            ("TOPPADDING", (0, 0), (-1, -1), 2 * mm),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2 * mm),
            ("LEFTPADDING", (0, 0), (-1, -1), 4 * mm),
        ]))
        story.append(feat_table)

    # ── Technical specs
    if sheet.technical_specs:
        story.append(Paragraph("Technical Specifications", s["section_heading"]))
        spec_data = [
            [
                Paragraph(spec.label, s["meta_label"]),
                Paragraph(spec.value, s["meta_value"]),
            ]
            for spec in sheet.technical_specs
        ]
        spec_table = Table(spec_data, colWidths=[60 * mm, doc.width - 60 * mm])
        spec_table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DDDDDD")),
            ("BACKGROUND", (0, 0), (0, -1), LIGHT_BG),
            ("TOPPADDING", (0, 0), (-1, -1), 2.5 * mm),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5 * mm),
            ("LEFTPADDING", (0, 0), (-1, -1), 3 * mm),
        ]))
        story.append(spec_table)

    # ── SEO section
    story.append(Paragraph("SEO Assets", s["section_heading"]))
    seo_content = [
        [Paragraph("Meta Title", s["meta_label"]), Paragraph(sheet.meta_title, s["meta_value"])],
        [Paragraph("Meta Description", s["meta_label"]), Paragraph(sheet.meta_description, s["meta_value"])],
        [
            Paragraph("Keywords", s["meta_label"]),
            Paragraph("  ·  ".join(sheet.seo_keywords), s["meta_value"]),
        ],
    ]
    seo_table = Table(seo_content, colWidths=[35 * mm, doc.width - 35 * mm])
    seo_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), KEYWORD_BG),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCEE")),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5 * mm),
        ("LEFTPADDING", (0, 0), (-1, -1), 3 * mm),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(seo_table)

    # ── Target audience
    story.append(Paragraph("Target Audience", s["section_heading"]))
    story.append(Paragraph(sheet.target_audience, s["body"]))

    # ── Footer
    story.append(Spacer(1, 8 * mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CCCCCC")))
    story.append(Spacer(1, 2 * mm))
    generated_at = sheet.generated_at.strftime("%Y-%m-%d %H:%M UTC") if sheet.generated_at else ""
    story.append(Paragraph(
        f"Generated by AI Product Sheet Generator · {generated_at} · Tone: {sheet.tone.value} · Language: {sheet.language.value}",
        s["footer"],
    ))

    doc.build(story)
    return buffer.getvalue()
