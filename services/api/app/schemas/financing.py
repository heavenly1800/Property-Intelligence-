from typing import Literal
from pydantic import BaseModel, Field

FinancingType = Literal["cash", "conventional", "dscr", "hard_money", "private", "seller_financing", "custom"]

class FinancingScenarioRequest(BaseModel):
    scenario_name: str = Field(min_length=1, max_length=120)
    financing_type: FinancingType
    purchase_price: float | None = Field(default=None, gt=0)
    down_payment_amount: float | None = Field(default=None, ge=0)
    down_payment_percentage: float | None = Field(default=None, ge=0, le=1)
    loan_amount: float | None = Field(default=None, ge=0)
    interest_rate: float | None = Field(default=None, ge=0, le=1)
    amortization_years: int | None = Field(default=None, gt=0)
    loan_term_months: int | None = Field(default=None, gt=0)
    interest_only_months: int = Field(default=0, ge=0)
    points_percentage: float = Field(default=0, ge=0)
    origination_fee: float = Field(default=0, ge=0)
    appraisal_fee: float = Field(default=0, ge=0)
    lender_fee: float = Field(default=0, ge=0)
    other_financing_costs: float = Field(default=0, ge=0)
    balloon_payment_month: int | None = Field(default=None, gt=0)
    prepayment_penalty: float = Field(default=0, ge=0)
    closing_costs_financed: bool = False
    rehab_financed_amount: float = Field(default=0, ge=0)
    reserve_requirement: float = Field(default=0, ge=0)
    notes: str | None = None
    is_approved: bool = False

class FinancingScenarioPatch(BaseModel):
    scenario_name: str | None = Field(default=None, min_length=1, max_length=120)
    financing_type: FinancingType | None = None
    purchase_price: float | None = Field(default=None, gt=0)
    down_payment_amount: float | None = Field(default=None, ge=0)
    down_payment_percentage: float | None = Field(default=None, ge=0, le=1)
    loan_amount: float | None = Field(default=None, ge=0)
    interest_rate: float | None = Field(default=None, ge=0, le=1)
    amortization_years: int | None = Field(default=None, gt=0)
    loan_term_months: int | None = Field(default=None, gt=0)
    interest_only_months: int | None = Field(default=None, ge=0)
    points_percentage: float | None = Field(default=None, ge=0)
    origination_fee: float | None = Field(default=None, ge=0)
    appraisal_fee: float | None = Field(default=None, ge=0)
    lender_fee: float | None = Field(default=None, ge=0)
    other_financing_costs: float | None = Field(default=None, ge=0)
    balloon_payment_month: int | None = Field(default=None, gt=0)
    prepayment_penalty: float | None = Field(default=None, ge=0)
    closing_costs_financed: bool | None = None
    rehab_financed_amount: float | None = Field(default=None, ge=0)
    reserve_requirement: float | None = Field(default=None, ge=0)
    notes: str | None = None
    is_approved: bool | None = None
