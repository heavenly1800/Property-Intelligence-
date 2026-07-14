from __future__ import annotations

from app.models.property_intelligence_report import (
    PropertyIntelligenceReport,
)
from app.pipeline.resolver import PropertyResolver


class EvidenceCollector:
    """
    Collects authoritative evidence for a property.
    """

    def __init__(self):
        self.resolver = PropertyResolver()

    def collect(
        self,
        property_data: dict,
    ) -> PropertyIntelligenceReport:

        report = PropertyIntelligenceReport()

        location = self.resolver.resolve(property_data)

        report.identity.completed = True
        report.identity.confidence = 100

        report.identity.data = {
            "address": property_data.get("address"),
            "city": property_data.get("city"),
            "state": property_data.get("state"),
            "county": location.county,
            "latitude": location.latitude,
            "longitude": location.longitude,
        }

        report.identity.evidence.append(
            "U.S. Census Geocoder"
        )

        return report