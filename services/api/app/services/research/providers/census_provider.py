from typing import Any

import httpx

from .base import ResearchProvider
from .models import (
    ResearchProviderResult,
    ResearchProviderStatus,
)


class CensusProvider(ResearchProvider):
    BASE_URL = (
        "https://geocoding.geo.census.gov/"
        "geocoder/geographies/onelineaddress"
    )

    async def execute(
        self,
        property_data: dict[str, Any],
    ) -> ResearchProviderResult:
        parts = [
            property_data.get("address"),
            property_data.get("city"),
            property_data.get("state"),
            property_data.get("zip_code"),
        ]

        address = ", ".join(
            str(part).strip()
            for part in parts
            if part
        )

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
                        "vintage": "Current_Current",
                        "format": "json",
                    },
                )

            response.raise_for_status()

            matches = (
                response.json()
                .get("result", {})
                .get("addressMatches", [])
            )

            if not matches:
                return ResearchProviderResult(
                    provider="Census",
                    status=ResearchProviderStatus.FAILED,
                    message="No Census address match found.",
                )

            match = matches[0]
            coordinates = match["coordinates"]
            geographies = match.get("geographies", {})

            county = None
            tract = None
            block_group = None

            counties = geographies.get("Counties", [])

            if counties:
                county = counties[0].get("NAME")

            for geography_items in geographies.values():
                if not geography_items:
                    continue

                geography = geography_items[0]

                if tract is None:
                    tract = geography.get("TRACT")

                if block_group is None:
                    block_group = geography.get("BLKGRP")

            return ResearchProviderResult(
                provider="Census",
                status=ResearchProviderStatus.COMPLETED,
                confidence=1.0,
                data={
                    "matched_address": match["matchedAddress"],
                    "latitude": coordinates["y"],
                    "longitude": coordinates["x"],
                    "county": county,
                    "census_tract": tract,
                    "block_group": block_group,
                },
            )

        except Exception as exc:
            return ResearchProviderResult(
                provider="Census",
                status=ResearchProviderStatus.FAILED,
                message=str(exc),
            )