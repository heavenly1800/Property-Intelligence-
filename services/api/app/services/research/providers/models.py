from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ResearchProviderStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ResearchProviderResult(BaseModel):
    provider: str
    status: ResearchProviderStatus
    data: dict[str, Any] = Field(default_factory=dict)
    message: str | None = None
    confidence: float = 0.0


class ResearchQualitySummary(BaseModel):
    research_quality_score: int
    parcel_certainty: str
    assessment_coverage: str
    utility_confidence: str
    research_risk_level: str
    missing_research_items: list[str] = Field(default_factory=list)
    recommended_research_action: str


class ResearchResult(BaseModel):
    providers: list[ResearchProviderResult] = Field(default_factory=list)
    completed_providers: list[str] = Field(default_factory=list)
    failed_providers: list[str] = Field(default_factory=list)
    progress: int = 0
    completed: bool = False
    confidence: float = 0.0
    quality_summary: ResearchQualitySummary | None = None
