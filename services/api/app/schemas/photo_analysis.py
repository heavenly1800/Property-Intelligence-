from typing import Literal

from pydantic import BaseModel, Field


ConditionRating = Literal["excellent", "good", "fair", "poor", "severe", "unknown"]
RentReadyStatus = Literal["ready", "minor_work", "substantial_work", "unknown"]
Severity = Literal["minor", "moderate", "major", "severe", "unknown"]


class ObservedIssue(BaseModel):
    category: str
    description: str
    severity: Severity
    visible_evidence: str
    recommended_action: str
    confidence: float = Field(ge=0, le=1)


class InferredIssue(BaseModel):
    category: str
    description: str
    basis: str
    recommended_inspection: str
    confidence: float = Field(ge=0, le=1)


class InspectionItem(BaseModel):
    category: str
    description: str
    reason: str


class RepairItem(BaseModel):
    category: str
    description: str
    area: str
    scope_units: int | None = Field(default=None, ge=1, le=20)
    estimated_quantity_low: float | None = Field(default=None, ge=0)
    estimated_quantity_high: float | None = Field(default=None, ge=0)
    quantity_unit: str | None = None
    quantity_confidence: float = Field(default=0.35, ge=0, le=1)


class PhotoConditionOutput(BaseModel):
    room_or_area: str
    visible_condition_summary: str
    condition_rating: ConditionRating
    observed_issues: list[ObservedIssue]
    inferred_issues: list[InferredIssue]
    unknown_inspection_items: list[InspectionItem]
    estimated_repair_items: list[RepairItem]
    rent_ready_status: RentReadyStatus
    safety_concerns: list[str]
    analysis_confidence: float = Field(ge=0, le=1)
    limitations: list[str]
