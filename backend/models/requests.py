from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from .product_sheet import Tone, Language


class GenerateRequest(BaseModel):
    product_name: str = Field(min_length=2, max_length=200)
    category: str = Field(min_length=2, max_length=100)
    source_url: Optional[str] = Field(default=None, description="URL to scrape for product context")
    raw_description: Optional[str] = Field(default=None, max_length=5000, description="Existing product description to enrich")
    target_audience: str = Field(min_length=5, max_length=500)
    tone: Tone = Tone.PROFESSIONAL
    language: Language = Language.EN
    additional_context: Optional[str] = Field(default=None, max_length=1000)
