import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.models.requests import GenerateRequest
from backend.models.product_sheet import Tone, Language


@pytest.fixture
def sample_request():
    return GenerateRequest(
        product_name="Sony WH-1000XM5",
        category="Wireless Headphones",
        target_audience="Remote workers and frequent travellers aged 25-45",
        tone=Tone.PROFESSIONAL,
        language=Language.EN,
    )


@pytest.fixture
def mock_llm():
    """A mock LLM that returns a preset response."""
    llm = AsyncMock()
    llm.ainvoke = AsyncMock(return_value=MagicMock(content='{"title": "Test", "tagline": "Test tagline", "short_description": "Short.", "full_description": "Full description paragraph."}'))
    return llm
