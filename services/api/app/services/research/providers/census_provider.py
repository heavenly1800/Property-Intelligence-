from typing import Any

import httpx

from .base import ResearchProvider
from .models import ResearchProviderResult, ResearchProviderStatus


class CensusProvider(ResearchProvider):
    BASE_URL = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"

    async def execute(
        self, property_data: dict[str, Any]
    ) -> ResearchProviderResult:
        address = property_data.get("address")

        if not address:
            return ResearchProviderResult(
                provider="Census",
                status=ResearchProviderStatus.SKIPPED,
                message="Property address is unavailable.",
            )

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.get(
                    self.BASE_URL,
                    params={
                        "address": address,
                        "benchmark": "Public_AR_Current",
                        "format": "json",
                    },
                )

            response.raise_for_status()

            matches = response.json()["result"]["addressMatches"]

            if not matches:
                return ResearchProviderResult(
                    provider="Census",
                    status=ResearchProviderStatus.FAILED,
                    message="No Census address match found.",
                )

            match = matches[0]

            return ResearchProviderResult(
                provider="Census",
                status=ResearchProviderStatus.COMPLETED,
                confidence=0.9,
                data={
                    "matched_address": match["matchedAddress"],
                    "latitude": match["coordinates"]["y"],
                    "longitude": match["coordinates"]["x"],
                },
            )

        except Exception as e:
            return ResearchProviderResult(
                provider="Census",
                status=ResearchProviderStatus.FAILED,
                message=str(e),
            )
