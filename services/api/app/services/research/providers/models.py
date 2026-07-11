from typing import Optional

from pydantic import BaseModel, Field


class ResearchResult(BaseModel):
    # Location
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    county: Optional[str] = None
    state: Optional[str] = None

    # Parcel
    apn: Optional[str] = None
    zoning: Optional[str] = None
    acreage: Optional[float] = None

    # Ownership
    owner_name: Optional[str] = None

    # Environmental
    flood_zone: Optional[str] = None

    # Infrastructure
    utilities_available: Optional[bool] = None

    # Research Metadata
    confidence: float = 0.0

    provider_status: dict[str, str] = Field(default_factory=dict)