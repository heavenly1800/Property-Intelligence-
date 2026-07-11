from typing import Any

import httpx

from .base import ResearchProvider


class CensusProvider(ResearchProvider):
    BASE_URL = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"

    async def research(self, property_data: dict[str, Any]) -> dict[str, Any]:
        address = property_data.get("address")

        if not address:
            return {}

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
                return {
                    "research_status": "No Census match found."
                }

            match = matches[0]

            return {
                "research_status": "Success",
                "matched_address": match["matchedAddress"],
                "latitude": match["coordinates"]["y"],
                "longitude": match["coordinates"]["x"],
            }

        except Exception as e:
            return {
                "research_status": "Failed",
                "research_error": str(e),
            }