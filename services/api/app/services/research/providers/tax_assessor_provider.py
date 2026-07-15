from dataclasses import dataclass
from typing import Any

import httpx

from .base import ResearchProvider
from .models import ResearchProviderResult, ResearchProviderStatus


@dataclass(frozen=True)
class AssessorService:
    query_url: str
    source: str
    apn_field: str
    fields: str


class TaxAssessorProvider(ResearchProvider):
    SAN_BERNARDINO_SERVICE = AssessorService(
        query_url=(
            "https://services.arcgis.com/aA3snZwJfFkVyDuP/arcgis/rest/"
            "services/Parcels_for_San_Bernardino_County/FeatureServer/0/query"
        ),
        source="San Bernardino County Public Parcel Viewer",
        apn_field="ParcelNumber",
        fields=(
            "ParcelNumber,OwnerName,LandValue,ImprovementValue,"
            "TaxStatus,Jurisdiction,AssessDescription"
        ),
    )
    SERVICES = {
        ("CA", "SAN BERNARDINO"): SAN_BERNARDINO_SERVICE,
    }

    async def execute(
        self, property_data: dict[str, Any]
    ) -> ResearchProviderResult:
        apn = self._value(property_data.get("apn"))
        county = self._normalize_county(property_data.get("county"))
        state = self._normalize_state(property_data.get("state"))

        if not apn:
            return self._skipped("Property APN is unavailable.")

        if not county or not state:
            return self._skipped(
                "Property county and state are required for assessor research."
            )

        service = self.SERVICES.get((state, county))

        if service is None:
            return self._skipped(
                f"Tax assessor research is not yet supported for {county.title()} County, {state}."
            )

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.get(
                    service.query_url,
                    params={
                        "where": self._where_clause(service.apn_field, apn),
                        "outFields": service.fields,
                        "returnGeometry": "false",
                        "f": "json",
                    },
                )

            response.raise_for_status()
            attributes = self._assessor_attributes(response.json())
        except (
            httpx.HTTPError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
        ) as error:
            return ResearchProviderResult(
                provider="Tax Assessor",
                status=ResearchProviderStatus.FAILED,
                message=f"Tax assessor request failed: {error}",
            )

        if attributes is None:
            return ResearchProviderResult(
                provider="Tax Assessor",
                status=ResearchProviderStatus.FAILED,
                message="No assessor record was found for this APN.",
            )

        land_value = self._currency(attributes.get("LandValue"))
        improvement_value = self._currency(
            attributes.get("ImprovementValue")
        )
        owner_name = self._public_owner(attributes.get("OwnerName"))
        tax_status = self._value(attributes.get("TaxStatus"))

        if not any(
            value is not None
            for value in (owner_name, land_value, improvement_value, tax_status)
        ):
            return ResearchProviderResult(
                provider="Tax Assessor",
                status=ResearchProviderStatus.FAILED,
                message="County assessor record did not include usable assessment data.",
            )

        return ResearchProviderResult(
            provider="Tax Assessor",
            status=ResearchProviderStatus.COMPLETED,
            confidence=1.0,
            data={
                "owner_name": owner_name,
                "assessed_land_value": land_value,
                "assessed_improvement_value": improvement_value,
                "assessed_total_value": (
                    land_value + improvement_value
                    if land_value is not None and improvement_value is not None
                    else None
                ),
                "tax_status": tax_status,
                "assessor_source": service.source,
            },
        )

    @staticmethod
    def _where_clause(field: str, apn: str) -> str:
        escaped_apn = apn.replace("'", "''")
        return f"{field} = '{escaped_apn}'"

    @staticmethod
    def _assessor_attributes(payload: Any) -> dict[str, Any] | None:
        if not isinstance(payload, dict):
            raise ValueError("Tax assessor returned an invalid response payload.")

        if payload.get("error"):
            raise ValueError(
                payload["error"].get("message", "Tax assessor query failed.")
            )

        features = payload.get("features")

        if not isinstance(features, list) or not features:
            return None

        feature = features[0]

        if not isinstance(feature, dict):
            raise ValueError("Tax assessor returned an invalid record.")

        attributes = feature.get("attributes")

        if not isinstance(attributes, dict):
            raise ValueError("Tax assessor returned invalid record attributes.")

        return attributes

    @staticmethod
    def _currency(value: Any) -> float | None:
        if isinstance(value, (int, float)):
            return float(value)

        if not isinstance(value, str) or not value.strip():
            return None

        try:
            return float(value.replace("$", "").replace(",", "").strip())
        except ValueError:
            return None

    @staticmethod
    def _public_owner(value: Any) -> str | None:
        owner = TaxAssessorProvider._value(value)

        if owner and owner.upper().startswith("PROTECTED PER"):
            return None

        return owner

    @staticmethod
    def _value(value: Any) -> str | None:
        if not isinstance(value, str):
            return None

        normalized = value.strip()
        return normalized or None

    @staticmethod
    def _normalize_county(value: Any) -> str | None:
        county = TaxAssessorProvider._value(value)
        return county.upper().removesuffix(" COUNTY").strip() if county else None

    @staticmethod
    def _normalize_state(value: Any) -> str | None:
        state = TaxAssessorProvider._value(value)

        if state is None:
            return None

        normalized = state.upper()
        return "CA" if normalized in {"CA", "CALIFORNIA"} else normalized

    @staticmethod
    def _skipped(message: str) -> ResearchProviderResult:
        return ResearchProviderResult(
            provider="Tax Assessor",
            status=ResearchProviderStatus.SKIPPED,
            message=message,
        )
