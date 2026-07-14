from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class BuyerScore(BaseModel):
    overall_score: float = Field(ge=0, le=100)

    distance_score: float = Field(default=0, ge=0, le=100)
    county_score: float = Field(default=0, ge=0, le=100)
    purchase_frequency_score: float = Field(default=0, ge=0, le=100)
    recency_score: float = Field(default=0, ge=0, le=100)
    property_type_score: float = Field(default=0, ge=0, le=100)
    acreage_score: float = Field(default=0, ge=0, le=100)


class BuyerMatch(BaseModel):
    buyer_name: str

    score: BuyerScore

    strengths: List[str] = Field(default_factory=list)
    concerns: List[str] = Field(default_factory=list)

    recommendation: Optional[str] = None

    purchase_count: int = 0
    confidence: float = 0


class BuyerMatchResult(BaseModel):
    buyers: List[BuyerMatch] = Field(default_factory=list)

    recommended_buyer: Optional[BuyerMatch] = None

    average_confidence: float = 0

    market_demand: str = "Unknown"

    generated_at: datetime = Field(default_factory=datetime.utcnow)