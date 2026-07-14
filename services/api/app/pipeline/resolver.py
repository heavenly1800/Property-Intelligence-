from __future__ import annotations

from app.models.location import Location
from app.providers.census.geocoder import CensusGeocoderProvider


class PropertyResolver:
    """
    Resolves the canonical location for a property.
    """

    def __init__(self):
        self.provider = CensusGeocoderProvider()

    def resolve(
        self,
        property_data: dict,
    ) -> Location:
        return self.provider.fetch(property_data)