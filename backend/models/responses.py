from pydantic import BaseModel
from typing import Optional
from .product_sheet import ProductSheet


class GenerateResponse(BaseModel):
    success: bool
    product_sheet: Optional[ProductSheet] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    model: str
    provider: str
