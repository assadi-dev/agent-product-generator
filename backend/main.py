from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.config import settings
from backend.logging_config import setup_logging, get_logger
from backend.api.routes.health import router as health_router
from backend.api.routes.generate import router as generate_router
from backend.api.routes.export import router as export_router

setup_logging(log_level=settings.log_level, log_format=settings.log_format)
logger = get_logger(__name__)

app = FastAPI(
    title="Product Sheet Generator API",
    description="AI-powered product sheet generator using LangGraph agent",
    version="0.1.0",
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(
        "unhandled_exception",
        method=request.method,
        path=request.url.path,
        error=str(exc),
        exc_info=True,
    )
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api/v1", tags=["health"])
app.include_router(generate_router, prefix="/api/v1", tags=["generate"])
app.include_router(export_router, prefix="/api/v1", tags=["export"])
