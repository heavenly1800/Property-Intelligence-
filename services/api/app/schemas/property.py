from typing import Optional

from pydantic import BaseModel


class PropertyResponse(BaseModel):
    property_id: str
    address: str

    city: Optional[str] = None
    county: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None

    property_type: Optional[str] = None

    apn: Optional[str] = None
    acres: Optional[float] = None
    square_feet: Optional[int] = None
    zoning: Optional[str] = None

    latitude: Optional[float] = None
    longitude: Optional[float] = None
    census_tract: Optional[str] = None
    block_group: Optional[str] = None
    flood_zone: Optional[str] = None
    flood_zone_subtype: Optional[str] = None
    special_flood_hazard_area: Optional[bool] = None
    flood_risk_level: Optional[str] = None
    flood_source: Optional[str] = None
    parcel_acres: Optional[float] = None
    jurisdiction: Optional[str] = None
    land_use: Optional[str] = None
    parcel_source: Optional[str] = None
    owner_name: Optional[str] = None
    owner_mailing_address: Optional[str] = None
    assessed_land_value: Optional[float] = None
    assessed_improvement_value: Optional[float] = None
    assessed_total_value: Optional[float] = None
    tax_year: Optional[int] = None
    tax_status: Optional[str] = None
    last_transfer_date: Optional[str] = None
    last_transfer_price: Optional[float] = None
    assessor_source: Optional[str] = None
