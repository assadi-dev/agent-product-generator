import json
from langchain_core.tools import tool
from backend.models.product_sheet import ProductSheet, TechnicalSpec, Tone, Language
from backend.models.requests import GenerateRequest


@tool
def format_product_sheet(
    product_name: str,
    category: str,
    language: str,
    tone: str,
    title: str,
    tagline: str,
    short_description: str,
    full_description: str,
    key_features: list[str],
    technical_specs: list[dict],
    target_audience: str,
    seo_keywords: list[str],
    meta_title: str,
    meta_description: str,
    source_url: str = "",
) -> str:
    """
    Assembles all generated components into a validated ProductSheet.
    ALWAYS call this tool LAST to finalize the product sheet.
    Arguments:
      - product_name, category, language, tone: from the original request
      - title, tagline, short_description, full_description: from generate_product_description / adapt_tone
      - key_features: list of strings from extract_key_features
      - technical_specs: list of {"label": "...", "value": "..."} dicts
      - target_audience: from original request
      - seo_keywords: list of strings from extract_seo_keywords
      - meta_title, meta_description: from extract_seo_keywords
      - source_url: optional, pass empty string if none
    Returns the serialized ProductSheet as a JSON string.
    """
    specs = [TechnicalSpec(label=s["label"], value=s["value"]) for s in (technical_specs or [])]

    sheet = ProductSheet(
        product_name=product_name,
        category=category,
        language=Language(language),
        tone=Tone(tone),
        title=title[:80],
        tagline=tagline[:120],
        short_description=short_description,
        full_description=full_description,
        key_features=key_features[:8],
        technical_specs=specs,
        target_audience=target_audience,
        seo_keywords=seo_keywords[:15],
        meta_title=meta_title[:60],
        meta_description=meta_description[:155],
        source_url=source_url or None,
    )
    return sheet.model_dump_json()
