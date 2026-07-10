from dataclasses import dataclass
from typing import Optional


@dataclass
class Property:

    property_id: str

    apn: Optional[str]

    address: str

    city: str

    county: str

    state: str

    zip_code: str

    property_type: str

    acres: Optional[float]

    square_feet: Optional[int]

    zoning: Optional[str]