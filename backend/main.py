from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.api.routes.health import router as health_router
from backend.api.routes.generate import router as generate_router
from backend.api.routes.export import router as export_router

app = FastAPI(
    title="Product Sheet Generator API",
    description="AI-powered product sheet generator using LangGraph agent",
    version="0.1.0",
)

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
