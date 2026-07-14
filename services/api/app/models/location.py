from dataclasses import dataclass
from typing import Optional


@dataclass
class Location:
    """
    Canonical geographic identity for a property.

    Everything in Property Intelligence begins here.
    """

    latitude: Optional[float] = None

    longitude: Optional[float] = None

    county: Optional[str] = None

    state: Optional[str] = None

    country: str = "US"

    census_tract: Optional[str] = None

    parcel_id: Optional[str] = None