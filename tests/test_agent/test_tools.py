"""
Unit tests for agent tools with mocked LLM responses.
"""
import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


@pytest.mark.asyncio
async def test_description_generator_returns_json(sample_request):
    """generate_product_description should return valid JSON with expected keys."""
    mock_response = MagicMock()
    mock_response.content = json.dumps({
        "title": "Sony WH-1000XM5 — Industry-Leading Noise Cancellation",
        "tagline": "Silence the world. Hear only what matters.",
        "short_description": "Premium wireless headphones designed for professionals.",
        "full_description": "Paragraph one.\n\nParagraph two.",
    })

    with patch("backend.agent.tools.description_generator.get_llm") as mock_get_llm:
        mock_llm = AsyncMock()
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)
        mock_get_llm.return_value = mock_llm

        from backend.agent.tools.description_generator import generate_product_description
        result = await generate_product_description.ainvoke({
            "product_name": sample_request.product_name,
            "category": sample_request.category,
            "context": "No extra context.",
            "tone": sample_request.tone.value,
            "language": sample_request.language.value,
        })

    data = json.loads(result)
    assert "title" in data
    assert "full_description" in data
    assert "short_description" in data


@pytest.mark.asyncio
async def test_feature_extractor_returns_list(sample_request):
    """extract_key_features should return a JSON array of strings."""
    mock_response = MagicMock()
    mock_response.content = json.dumps([
        "30-hour battery life",
        "Industry-leading active noise cancellation",
        "Multipoint Bluetooth connection",
    ])

    with patch("backend.agent.tools.feature_extractor.get_llm") as mock_get_llm:
        mock_llm = AsyncMock()
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)
        mock_get_llm.return_value = mock_llm

        from backend.agent.tools.feature_extractor import extract_key_features
        result = await extract_key_features.ainvoke({
            "product_name": sample_request.product_name,
            "category": sample_request.category,
            "product_description": "Excellent headphones with great features.",
        })

    features = json.loads(result)
    assert isinstance(features, list)
    assert len(features) >= 1


def test_structured_formatter_produces_valid_sheet():
    """format_product_sheet should return a valid ProductSheet JSON string."""
    from backend.agent.tools.structured_formatter import format_product_sheet

    result = format_product_sheet.invoke({
        "product_name": "Sony WH-1000XM5",
        "category": "Wireless Headphones",
        "language": "en",
        "tone": "professional",
        "title": "Sony WH-1000XM5 — Premium Noise Cancellation",
        "tagline": "Silence the world. Hear what matters.",
        "short_description": "Top-tier wireless headphones.",
        "full_description": "Long description here.\n\nSecond paragraph.",
        "key_features": ["30-hour battery", "ANC", "Multipoint"],
        "technical_specs": [{"label": "Battery", "value": "30h"}],
        "target_audience": "Remote workers aged 25-45",
        "seo_keywords": ["noise cancelling headphones", "wireless headphones"],
        "meta_title": "Sony WH-1000XM5 Headphones",
        "meta_description": "Best noise cancelling headphones for professionals.",
        "source_url": "",
    })

    from backend.models.product_sheet import ProductSheet
    sheet = ProductSheet.model_validate_json(result)
    assert sheet.product_name == "Sony WH-1000XM5"
    assert len(sheet.key_features) == 3
    assert sheet.language.value == "en"
