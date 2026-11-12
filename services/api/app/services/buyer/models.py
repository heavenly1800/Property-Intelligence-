from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

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

    score: Optional[BuyerScore] = None

    strengths: List[str] = Field(default_factory=list)
    concerns: List[str] = Field(default_factory=list)

    recommendation: Optional[str] = None

    purchase_count: Optional[int] = None
    confidence: Optional[float] = None


class BuyerMatchResult(BaseModel):
    buyers: List[BuyerMatch] = Field(default_factory=list)

    recommended_buyer: Optional[BuyerMatch] = None

    average_confidence: Optional[float] = None

    market_demand: str = "Unknown"

    status: Literal["verified_buyers_found", "no_verified_buyers"] = (
        "no_verified_buyers"
    )
    message: str = "No verified buyers found."

    generated_at: datetime = Field(default_factory=datetime.utcnow)
