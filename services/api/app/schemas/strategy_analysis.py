from typing import Literal

from pydantic import BaseModel, Field


StrategyName = Literal["wholesale", "wholetail", "flip", "rental_hold"]


class StrategyResult(BaseModel):
    strategy: StrategyName
    viable: bool
    rank: int | None = None
    score: float = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=1)
    acquisition_price_used: float | None = None
    value_basis: str | None = None
    value_low: float | None = None
    value_high: float | None = None
    rehab_cost_low: float | None = None
    rehab_cost_high: float | None = None
    holding_costs: float | None = None
    closing_costs: float | None = None
    selling_costs: float | None = None
    projected_revenue_low: float | None = None
    projected_revenue_high: float | None = None
    projected_profit_low: float | None = None
    projected_profit_high: float | None = None
    projected_return_percentage_low: float | None = None
    projected_return_percentage_high: float | None = None
    monthly_cash_flow: float | None = None
    annual_cash_flow: float | None = None
    cap_rate: float | None = None
    major_risks: list[str]
    strengths: list[str]
    missing_inputs: list[str]
    formula_notes: list[str]


class StrategyAnalysis(BaseModel):
    strategy_analysis_id: str | None = None
    property_id: str
    recommended_strategy: StrategyName | None = None
    recommendation_confidence: float = Field(ge=0, le=1)
    analysis_status: str
    analyzed_at: str
    assumptions_version: str
    missing_inputs: list[str]
    limitations: list[str]
    recommended_next_action: str
    input_snapshot: dict
    results: list[StrategyResult]
