from __future__ import annotations

from app.infrastructure.http.rentcast_client import RentCastClient

from app.core.settings import get_settings
from app.services.comparables.models import (
    ComparableResult,
)
from app.services.comparables.providers.base import (
    ComparableProvider,
)


class RentCastProvider(ComparableProvider):
    

    def __init__(self):
        self.settings = get_settings()
        self.client = RentCastClient()

    def search(
        self,
        property_data: dict,
    ) -> ComparableResult:

    

        #
        # Request implementation will be added
        # in the next sprint.
        #

       

        return ComparableResult(
            estimated_value=0,
            confidence=0,
            comparables=[],
        )