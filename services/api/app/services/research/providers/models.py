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


class ResearchResult(BaseModel):
    providers: list[ResearchProviderResult] = Field(default_factory=list)
    completed_providers: list[str] = Field(default_factory=list)
    failed_providers: list[str] = Field(default_factory=list)
    progress: int = 0
    completed: bool = False
    confidence: float = 0.0
