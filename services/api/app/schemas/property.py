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
