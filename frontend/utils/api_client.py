"""
HTTP client for the FastAPI backend.
All calls go through this module so the Streamlit pages stay clean.
"""
import json
import httpx
import os

BACKEND_URL = os.getenv("STREAMLIT_BACKEND_URL", "http://localhost:8000")


def generate_sync(payload: dict) -> dict:
    """Calls POST /api/v1/generate and returns the JSON response."""
    with httpx.Client(timeout=120) as client:
        resp = client.post(f"{BACKEND_URL}/api/v1/generate", json=payload)
        resp.raise_for_status()
        return resp.json()


def generate_stream(payload: dict):
    """
    Generator that yields parsed SSE event dicts from POST /api/v1/generate/stream.
    Each yielded item is a dict with at least a 'type' key.
    """
    with httpx.Client(timeout=180) as client:
        with client.stream("POST", f"{BACKEND_URL}/api/v1/generate/stream", json=payload) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if line.startswith("data: "):
                    raw = line[6:]
                    try:
                        yield json.loads(raw)
                    except json.JSONDecodeError:
                        continue


def export_json(sheet: dict) -> bytes:
    with httpx.Client(timeout=30) as client:
        resp = client.post(f"{BACKEND_URL}/api/v1/export/json", json=sheet)
        resp.raise_for_status()
        return resp.content


def export_pdf(sheet: dict) -> bytes:
    with httpx.Client(timeout=30) as client:
        resp = client.post(f"{BACKEND_URL}/api/v1/export/pdf", json=sheet)
        resp.raise_for_status()
        return resp.content


def health_check() -> dict:
    with httpx.Client(timeout=5) as client:
        resp = client.get(f"{BACKEND_URL}/api/v1/health")
        resp.raise_for_status()
        return resp.json()
