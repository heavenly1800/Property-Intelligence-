from typing import Literal

from pydantic import BaseModel, Field


OfferStrategy = Literal["wholesale", "wholetail", "flip", "rental_hold", "custom"]


class OfferCalculationRequest(BaseModel):
    selected_strategy: OfferStrategy | None = None
    allow_over_asking_offer: bool = False


class ManualOfferRequest(BaseModel):
    target_offer: float = Field(gt=0)
    target_margin: float | None = None
    notes: str | None = None


class OfferAnalysis(BaseModel):
    offer_analysis_id: str | None = None
    property_id: str
    selected_strategy: OfferStrategy
    offer_status: str
    recommended_offer_low: float | None = None
    recommended_offer: float | None = None
    recommended_offer_high: float | None = None
    maximum_allowable_offer: float | None = None
    seller_asking_price: float | None = None
    estimated_discount_to_asking: float | None = None
    offer_confidence: float = Field(ge=0, le=1)
    value_basis: str | None = None
    rehab_basis: str | None = None
    rent_basis: str | None = None
    assumptions_version: str
    input_snapshot: dict
    blockers: list[str]
    warnings: list[str]
    strengths: list[str]
    missing_inputs: list[str]
    limitations: list[str]
    formula_notes: list[str]
    projected_metric_label: str | None = None
    projected_metric_low: float | None = None
    projected_metric_high: float | None = None
    margin_to_mao: float | None = None
    allow_over_asking_offer: bool = False
    manual_target_margin: float | None = None
    manual_notes: str | None = None
    created_at: str | None = None
