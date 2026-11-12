from __future__ import annotations

from app.infrastructure.database.property_repository import PropertyRepository

from app.services.buyer.engine import BuyerEngine
from app.services.buyer.models import BuyerMatchResult


class BuyerService:
    """
    Public entry point for Buyer Intelligence.

    Responsible for:

    • Loading the subject property
    • Executing the legacy BuyerEngine
    • Scoring every buyer
    • Ranking buyers
    • Returning a standardized BuyerMatchResult
    """

    def __init__(self):
        self.repository = PropertyRepository()
        self.engine = BuyerEngine()

    def find_buyers(
        self,
        property_id: str,
    ) -> BuyerMatchResult | None:

        property_data = self.repository.get(property_id)

        if property_data is None:
            return None

        raw_buyers = self.engine.find_buyers(property_data)

        if not raw_buyers:
            return BuyerMatchResult()

        confidences = [
            buyer.confidence
            for buyer in raw_buyers
            if buyer.confidence is not None
        ]
        average = (
            round(sum(confidences) / len(confidences), 1)
            if confidences
            else None
        )

        return BuyerMatchResult(
            buyers=raw_buyers,
            average_confidence=average,
            status="verified_buyers_found",
            message="Verified buyers found.",
        )

    def get_matches(self, property_id: str) -> BuyerMatchResult | None:
        """Compatibility entry point for existing strategy analysis code."""
        return self.find_buyers(property_id)
