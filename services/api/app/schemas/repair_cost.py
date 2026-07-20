from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


UnitType = Literal["square foot", "linear foot", "per room", "per item", "per unit/apartment", "lump sum", "percentage contingency"]


class CostProfileInput(BaseModel):
    profile_name: str
    country: str = "US"
    state: str | None = None
    county: str | None = None
    city: str | None = None
    zip_code: str | None = None
    effective_date: date
    source_notes: str
    confidence: float = Field(ge=0, le=1)
    is_default: bool = False


class CostProfilePatch(BaseModel):
    profile_name: str | None = None
    country: str | None = None
    state: str | None = None
    county: str | None = None
    city: str | None = None
    zip_code: str | None = None
    effective_date: date | None = None
    source_notes: str | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)
    is_default: bool | None = None


class CostItemInput(BaseModel):
    category: str
    unit_type: UnitType
    cost_low_per_unit: float = Field(ge=0)
    cost_high_per_unit: float = Field(ge=0)
    minimum_job_cost_low: float = Field(ge=0)
    minimum_job_cost_high: float = Field(ge=0)
    labor_material_notes: str
    source_notes: str
    effective_date: date
    contingency_percentage: float = Field(default=0, ge=0, le=100)


class CostItemPatch(BaseModel):
    category: str | None = None
    unit_type: UnitType | None = None
    cost_low_per_unit: float | None = Field(default=None, ge=0)
    cost_high_per_unit: float | None = Field(default=None, ge=0)
    minimum_job_cost_low: float | None = Field(default=None, ge=0)
    minimum_job_cost_high: float | None = Field(default=None, ge=0)
    labor_material_notes: str | None = None
    source_notes: str | None = None
    effective_date: date | None = None
    contingency_percentage: float | None = Field(default=None, ge=0, le=100)
