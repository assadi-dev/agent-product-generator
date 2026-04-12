from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional
from datetime import datetime, timezone, timezone


class Tone(str, Enum):
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    LUXURY = "luxury"
    TECHNICAL = "technical"


class Language(str, Enum):
    EN = "en"
    FR = "fr"


class TechnicalSpec(BaseModel):
    label: str
    value: str


class ProductSheet(BaseModel):
    # Identity
    product_name: str
    category: str
    language: Language
    tone: Tone

    # Generated content
    title: str = Field(description="Punchy marketing title, max 80 chars")
    tagline: str = Field(description="One-sentence value proposition, max 120 chars")
    short_description: str = Field(description="2-3 sentence elevator pitch")
    full_description: str = Field(description="3-5 paragraph rich description")
    key_features: list[str] = Field(description="5-8 bullet feature points")
    technical_specs: list[TechnicalSpec] = Field(default_factory=list, description="Key-value spec pairs")
    target_audience: str = Field(description="Detailed target persona description")

    # SEO
    seo_keywords: list[str] = Field(description="10-15 SEO-optimized keywords")
    meta_title: str = Field(description="SEO meta title, max 60 chars")
    meta_description: str = Field(description="SEO meta description, max 155 chars")

    # Metadata
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    agent_trace: list[str] = Field(default_factory=list, description="Steps the agent took")
    source_url: Optional[str] = None
