from fastapi import APIRouter
from backend.models.responses import HealthResponse
from backend.config import settings
from backend.services.llm_factory import get_model_name

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="ok",
        model=get_model_name(),
        provider=settings.llm_provider,
    )
