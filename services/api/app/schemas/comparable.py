from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, model_validator


ComparableType = Literal["sale", "rental"]


class ComparableInput(BaseModel):
    comparable_type: ComparableType
    source_name: str
    source_url: str
    source_record_id: str | None = None
    address: str
    latitude: float | None = None
    longitude: float | None = None
    distance_miles: float | None = Field(default=None, ge=0)
    property_type: str
    property_subtype: str | None = None
    unit_count: int | None = Field(default=None, ge=1)
    bedrooms: float | None = Field(default=None, ge=0)
    bathrooms: float | None = Field(default=None, ge=0)
    square_feet: float | None = Field(default=None, gt=0)
    lot_acres: float | None = Field(default=None, ge=0)
    year_built: int | None = Field(default=None, ge=1700, le=2100)
    condition: str | None = None
    sale_price: float | None = Field(default=None, gt=0)
    sale_date: date | None = None
    monthly_rent: float | None = Field(default=None, gt=0)
    listing_date: date | None = None
    status: str | None = None
    included: bool = True
    notes: str | None = None

    @model_validator(mode="after")
    def validate_evidence(self):
        if self.comparable_type == "sale" and (self.sale_price is None or self.sale_date is None):
            raise ValueError("Sale comparables require sale_price and sale_date.")
        if self.comparable_type == "rental" and (self.monthly_rent is None or self.listing_date is None):
            raise ValueError("Rental comparables require monthly_rent and listing_date.")
        return self


class ComparablePatch(BaseModel):
    source_name: str | None = None
    source_url: str | None = None
    source_record_id: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    distance_miles: float | None = Field(default=None, ge=0)
    property_type: str | None = None
    property_subtype: str | None = None
    unit_count: int | None = Field(default=None, ge=1)
    bedrooms: float | None = Field(default=None, ge=0)
    bathrooms: float | None = Field(default=None, ge=0)
    square_feet: float | None = Field(default=None, gt=0)
    lot_acres: float | None = Field(default=None, ge=0)
    year_built: int | None = Field(default=None, ge=1700, le=2100)
    condition: str | None = None
    sale_price: float | None = Field(default=None, gt=0)
    sale_date: date | None = None
    monthly_rent: float | None = Field(default=None, gt=0)
    listing_date: date | None = None
    status: str | None = None
    included: bool | None = None
    notes: str | None = None
