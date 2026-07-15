from dataclasses import dataclass
from typing import Any

import httpx

from .base import ResearchProvider
from .models import ResearchProviderResult, ResearchProviderStatus


@dataclass(frozen=True)
class UtilityJurisdiction:
    source_url: str
    source: str
    electric_provider: str
    water_provider: str
    zip_codes: frozenset[str]


class UtilitiesProvider(ResearchProvider):
    """Researches public utility information from jurisdictional sources."""

    TWENTYNINE_PALMS = UtilityJurisdiction(
        source_url="https://www.ci.twentynine-palms.ca.us/faq",
        source=(
            "City of Twentynine Palms Utilities FAQ; "
            "FCC National Broadband Map"
        ),
        electric_provider="Southern California Edison",
        water_provider="Twentynine Palms Water District",
        zip_codes=frozenset({"92277"}),
    )
    JURISDICTIONS = {
        ("CA", "SAN BERNARDINO", "TWENTYNINE PALMS"): TWENTYNINE_PALMS,
    }
    FCC_BROADBAND_MAP_URL = "https://broadbandmap.fcc.gov/"

    async def execute(
        self, property_data: dict[str, Any]
    ) -> ResearchProviderResult:
        latitude = property_data.get("latitude")
        longitude = property_data.get("longitude")
        state = self._normalize(property_data.get("state"))
        county = self._normalize_county(property_data.get("county"))
        zip_code = self._normalize_zip(property_data.get("zip_code"))
        locality = self._normalize(
            property_data.get("jurisdiction") or property_data.get("city")
        )
        locality = self._normalize_locality(locality)

        if latitude is None or longitude is None:
            return self._skipped("Property coordinates are unavailable.")

        if not state or not county or not locality:
            return self._skipped(
                "Property jurisdiction, county, and state are required for utilities research."
            )

        jurisdiction = self.JURISDICTIONS.get((state, county, locality))

        if jurisdiction is None:
            return self._skipped(
                "Utilities research is not yet supported for this jurisdiction."
            )

        if zip_code and zip_code not in jurisdiction.zip_codes:
            return self._skipped(
                "Property ZIP code is outside this jurisdiction's configured utility profile."
            )

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.get(jurisdiction.source_url)
                response.raise_for_status()
            source_page = response.text
        except httpx.HTTPError as error:
            return ResearchProviderResult(
                provider="Utilities",
                status=ResearchProviderStatus.FAILED,
                message=f"Utilities source request failed: {error}",
            )

        if not self._contains_provider(source_page, jurisdiction.electric_provider):
            return self._failed("City utility source did not identify the electric provider.")

        if not self._contains_provider(source_page, jurisdiction.water_provider):
            return self._failed("City utility source did not identify the water provider.")

        return ResearchProviderResult(
            provider="Utilities",
            status=ResearchProviderStatus.COMPLETED,
            confidence=0.65,
            message=(
                "Electric and water providers are jurisdiction-level matches; "
                "verify service connection with each provider."
            ),
            data={
                "electric_provider": jurisdiction.electric_provider,
                "electric_service_evidence": "likely_jurisdiction",
                "water_provider": jurisdiction.water_provider,
                "water_service_evidence": "likely_jurisdiction",
                "gas_service_evidence": "unavailable_or_unverified",
                "sewer_service_evidence": "unavailable_or_unverified",
                "broadband_summary": (
                    "Unverified — search the official FCC National Broadband Map "
                    "by property address."
                ),
                "broadband_evidence": "unavailable_or_unverified",
                "utilities_source": jurisdiction.source,
            },
        )

    @staticmethod
    def _contains_provider(source_page: str, provider: str) -> bool:
        return provider.casefold() in source_page.casefold()

    @staticmethod
    def _normalize(value: Any) -> str | None:
        if not isinstance(value, str) or not value.strip():
            return None

        return value.strip().upper()

    @classmethod
    def _normalize_county(cls, value: Any) -> str | None:
        county = cls._normalize(value)
        return county.removesuffix(" COUNTY").strip() if county else None

    @staticmethod
    def _normalize_locality(value: str | None) -> str | None:
        if value is None:
            return None

        return value.removeprefix("CITY OF ").strip()

    @staticmethod
    def _normalize_zip(value: Any) -> str | None:
        if not isinstance(value, str):
            return None

        zip_code = value.strip()[:5]
        return zip_code if zip_code.isdigit() else None

    @staticmethod
    def _skipped(message: str) -> ResearchProviderResult:
        return ResearchProviderResult(
            provider="Utilities",
            status=ResearchProviderStatus.SKIPPED,
            message=message,
        )

    @staticmethod
    def _failed(message: str) -> ResearchProviderResult:
        return ResearchProviderResult(
            provider="Utilities",
            status=ResearchProviderStatus.FAILED,
            message=message,
        )
