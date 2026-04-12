"""
Integration tests for FastAPI routes using httpx.AsyncClient.
These tests mock the agent graph so they don't require a real API key.
"""
import json
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient, ASGITransport

from backend.main import app
from backend.models.product_sheet import ProductSheet, Tone, Language


def _mock_sheet() -> ProductSheet:
    return ProductSheet(
        product_name="Test Product",
        category="Electronics",
        language=Language.EN,
        tone=Tone.PROFESSIONAL,
        title="Test Product — The Best",
        tagline="Because you deserve the best.",
        short_description="A short description.",
        full_description="A much longer and detailed description of the product.",
        key_features=["Feature A", "Feature B", "Feature C"],
        technical_specs=[],
        target_audience="Tech-savvy professionals",
        seo_keywords=["test", "product", "electronics"],
        meta_title="Test Product",
        meta_description="Buy the best Test Product for professionals.",
        generated_at=datetime.now(timezone.utc),
    )


@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "model" in data


@pytest.mark.asyncio
async def test_generate_returns_product_sheet():
    mock_sheet = _mock_sheet()
    mock_final_state = {
        "product_sheet": mock_sheet,
        "agent_trace": ["Step 1", "Step 2"],
        "error": None,
    }

    mock_graph = AsyncMock()
    mock_graph.ainvoke = AsyncMock(return_value=mock_final_state)

    with patch("backend.agent.graph.build_graph", return_value=(mock_graph, "test-thread-id")):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/api/v1/generate", json={
                "product_name": "Test Product",
                "category": "Electronics",
                "target_audience": "Tech-savvy professionals",
                "tone": "professional",
                "language": "en",
            })

    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["product_sheet"]["product_name"] == "Test Product"


@pytest.mark.asyncio
async def test_export_json_returns_file():
    sheet = _mock_sheet()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/api/v1/export/json", json=sheet.model_dump(mode="json"))
    assert resp.status_code == 200
    assert "application/json" in resp.headers["content-type"]
    data = json.loads(resp.content)
    assert data["product_name"] == "Test Product"
