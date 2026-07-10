from pydantic import BaseModel
from typing import Optional


class PropertyResponse(BaseModel):
    property_id: str
    address: str
    city: str
    county: str
    state: str
    zip_code: str

    property_type: str

    apn: Optional[str] = None

    acres: Optional[float] = None

    square_feet: Optional[int] = None

    zoning: Optional[str] = None