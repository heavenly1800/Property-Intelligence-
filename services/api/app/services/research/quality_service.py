from typing import Any

from .providers.models import ResearchQualitySummary


class ResearchQualityService:
    """Applies transparent completeness rules to persisted research fields."""

    @classmethod
    def evaluate(cls, property_data: dict[str, Any]) -> ResearchQualitySummary:
        score = (
            cls._geography_score(property_data)
            + cls._parcel_score(property_data)
            + cls._fema_score(property_data)
            + cls._assessment_score(property_data)
            + cls._utilities_score(property_data)
        )
        parcel_certainty = cls._parcel_certainty(property_data)
        assessment_coverage = cls._assessment_coverage(property_data)
        utility_confidence = cls._utility_confidence(property_data)
        missing_items = cls._missing_items(property_data)
        risk_level = cls._risk_level(
            score,
            parcel_certainty,
            assessment_coverage,
            utility_confidence,
            property_data,
        )

        return ResearchQualitySummary(
            research_quality_score=score,
            parcel_certainty=parcel_certainty,
            assessment_coverage=assessment_coverage,
            utility_confidence=utility_confidence,
            research_risk_level=risk_level,
            missing_research_items=missing_items,
            recommended_research_action=cls._recommended_action(
                property_data,
                parcel_certainty,
                assessment_coverage,
                utility_confidence,
            ),
        )

    @staticmethod
    def _geography_score(data: dict[str, Any]) -> int:
        return sum(
            points
            for value, points in (
                (data.get("latitude") is not None and data.get("longitude") is not None, 8),
                (data.get("county"), 4),
                (data.get("census_tract"), 4),
                (data.get("block_group"), 4),
            )
            if value
        )

    @staticmethod
    def _parcel_score(data: dict[str, Any]) -> int:
        return sum(
            points
            for value, points in (
                (data.get("apn"), 8),
                (data.get("parcel_acres") is not None, 7),
                (data.get("zoning"), 5),
            )
            if value
        )

    @staticmethod
    def _fema_score(data: dict[str, Any]) -> int:
        return sum(
            points
            for value, points in (
                (data.get("flood_zone"), 8),
                (data.get("special_flood_hazard_area") is not None, 6),
                (data.get("flood_risk_level"), 6),
            )
            if value
        )

    @staticmethod
    def _assessment_score(data: dict[str, Any]) -> int:
        return sum(
            points
            for value, points in (
                (data.get("assessed_land_value") is not None, 5),
                (data.get("assessed_improvement_value") is not None, 5),
                (data.get("assessed_total_value") is not None, 5),
                (data.get("tax_status"), 5),
            )
            if value
        )

    @classmethod
    def _utilities_score(cls, data: dict[str, Any]) -> int:
        return (
            cls._evidence_points(data.get("electric_service_evidence"), 5)
            + cls._evidence_points(data.get("water_service_evidence"), 5)
            + cls._evidence_points(data.get("gas_service_evidence"), 3)
            + cls._evidence_points(data.get("sewer_service_evidence"), 5)
            + cls._evidence_points(data.get("broadband_evidence"), 2)
        )

    @staticmethod
    def _evidence_points(evidence: Any, maximum: int) -> int:
        if evidence == "confirmed_service_area":
            return maximum
        if evidence == "likely_jurisdiction":
            return max(1, round(maximum * 0.6))
        return 0

    @staticmethod
    def _parcel_certainty(data: dict[str, Any]) -> str:
        if (
            data.get("apn")
            and data.get("parcel_acres") is not None
            and data.get("zoning")
        ):
            return "high"
        if data.get("apn") and (data.get("parcel_acres") is not None or data.get("zoning")):
            return "medium"
        return "low"

    @staticmethod
    def _assessment_coverage(data: dict[str, Any]) -> str:
        fields = (
            "assessed_land_value",
            "assessed_improvement_value",
            "assessed_total_value",
            "tax_status",
        )
        present = sum(
            data.get(field) is not None and data.get(field) != ""
            for field in fields
        )
        if present == len(fields):
            return "complete"
        if present:
            return "partial"
        return "missing"

    @staticmethod
    def _utility_confidence(data: dict[str, Any]) -> str:
        electric = data.get("electric_service_evidence")
        water = data.get("water_service_evidence")
        sewer = data.get("sewer_service_evidence")
        if all(value == "confirmed_service_area" for value in (electric, water, sewer)):
            return "high"
        if electric in {"confirmed_service_area", "likely_jurisdiction"} and water in {
            "confirmed_service_area",
            "likely_jurisdiction",
        }:
            return "medium"
        return "low"

    @classmethod
    def _risk_level(
        cls,
        score: int,
        parcel_certainty: str,
        assessment_coverage: str,
        utility_confidence: str,
        data: dict[str, Any],
    ) -> str:
        has_fema_status = data.get("flood_zone") and data.get(
            "special_flood_hazard_area"
        ) is not None
        if score >= 80 and parcel_certainty == "high" and assessment_coverage == "complete" and utility_confidence != "low" and has_fema_status:
            return "low"
        if score < 60 or parcel_certainty == "low" or not has_fema_status:
            return "high"
        return "medium"

    @staticmethod
    def _missing_items(data: dict[str, Any]) -> list[str]:
        items: list[str] = []
        checks = (
            (data.get("latitude") is None or data.get("longitude") is None, "Property coordinates"),
            (not data.get("county"), "County"),
            (not data.get("census_tract"), "Census tract"),
            (not data.get("block_group"), "Census block group"),
            (not data.get("apn"), "APN"),
            (data.get("parcel_acres") is None, "Parcel acreage"),
            (not data.get("zoning"), "Zoning"),
            (not data.get("flood_zone"), "FEMA flood zone"),
            (data.get("special_flood_hazard_area") is None, "FEMA SFHA status"),
            (data.get("assessed_total_value") is None, "Assessed total value"),
            (not data.get("tax_status"), "Tax status"),
            (not data.get("owner_name"), "Public owner name unavailable (may be protected by law)"),
            (not data.get("last_transfer_date"), "Last transfer date"),
            (data.get("last_transfer_price") is None, "Last transfer price"),
            (not data.get("gas_provider"), "Gas provider"),
            (not data.get("sewer_provider"), "Sewer availability"),
            (data.get("broadband_evidence") in {None, "unavailable_or_unverified"}, "Broadband availability"),
        )
        return [item for missing, item in checks if missing]

    @staticmethod
    def _recommended_action(
        data: dict[str, Any],
        parcel_certainty: str,
        assessment_coverage: str,
        utility_confidence: str,
    ) -> str:
        if data.get("latitude") is None or data.get("longitude") is None:
            return "Resolve property coordinates before continuing research."
        if parcel_certainty == "low":
            return "Confirm the parcel APN through County GIS."
        if not data.get("flood_zone") or data.get("special_flood_hazard_area") is None:
            return "Verify FEMA flood zone and special flood hazard status."
        if assessment_coverage != "complete":
            return "Obtain county assessment and tax-status data."
        if utility_confidence == "low":
            return "Verify parcel-level utility service and connection availability."
        if not data.get("owner_name") or not data.get("last_transfer_date"):
            return "Verify public ownership and transfer history through county records."
        return "Research coverage is sufficient; verify acquisition assumptions before outreach."
