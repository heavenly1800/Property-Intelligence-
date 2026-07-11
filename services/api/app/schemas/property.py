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