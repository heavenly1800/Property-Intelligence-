from __future__ import annotations

from statistics import mean

from app.infrastructure.database.property_repository import PropertyRepository

from app.services.buyer.engine import BuyerEngine
from app.services.buyer.models import (
    BuyerMatch,
    BuyerMatchResult,
)
from app.services.buyer.scoring import score_buyer


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

    def get_matches(
        self,
        property_id: str,
    ) -> BuyerMatchResult:

        property_data = self.repository.get(property_id)

        raw_buyers = self.engine.find_buyers(property_data)

        matches: list[BuyerMatch] = []

        for buyer in raw_buyers:

            score = score_buyer(
                buyer,
                property_data,
            )

            strengths = []
            concerns = []

            if score.distance_score >= 80:
                strengths.append(
                    "Strong purchasing activity near this property."
                )

            if score.county_score >= 80:
                strengths.append(
                    "Frequently purchases properties in this county."
                )

            if score.purchase_frequency_score >= 80:
                strengths.append(
                    "High volume repeat buyer."
                )

            if score.purchase_frequency_score < 50:
                concerns.append(
                    "Limited purchase history."
                )

            if score.recency_score < 50:
                concerns.append(
                    "No recent acquisition activity."
                )

            recommendation = (
                "Contact First"
                if score.overall_score >= 85
                else "Strong Candidate"
                if score.overall_score >= 70
                else "Secondary Prospect"
            )

            matches.append(
                BuyerMatch(
                    buyer_name=buyer["buyer_name"],
                    purchase_count=buyer.get(
                        "purchase_count",
                        0,
                    ),
                    confidence=buyer.get(
                        "confidence",
                        score.overall_score,
                    ),
                    score=score,
                    strengths=strengths,
                    concerns=concerns,
                    recommendation=recommendation,
                )
            )

        matches.sort(
            key=lambda m: m.score.overall_score,
            reverse=True,
        )

        average = (
            mean(
                [
                    m.score.overall_score
                    for m in matches
                ]
            )
            if matches
            else 0
        )

        demand = (
            "High"
            if average >= 80
            else "Moderate"
            if average >= 60
            else "Low"
        )

        return BuyerMatchResult(
            buyers=matches,
            recommended_buyer=matches[0]
            if matches
            else None,
            average_confidence=round(
                average,
                1,
            ),
            market_demand=demand,
        )