from scoring import DealScorer


class DealEngine:
    """
    Central engine responsible for evaluating a deal.
    """

    def __init__(self):
        self.scorer = DealScorer()

    def evaluate(self, property_data: dict):
        deal = self.scorer.score(property_data)

        # Placeholder values until the Market Engine
        # and Buyer Engine are fully integrated.
        deal.strategy = "Wholesale Assignment"

        deal.market_value = None
        deal.recommended_offer = None
        deal.assignment_fee = None

        if deal.overall_score >= 85:
            deal.recommended_actions = [
                "Contact the seller immediately.",
                "Run buyer discovery.",
                "Prepare an offer.",
            ]

            deal.ai_summary = (
                "This appears to be a strong acquisition candidate "
                "based on currently available information."
            )

        elif deal.overall_score >= 70:
            deal.recommended_actions = [
                "Complete additional research.",
                "Verify ownership and utilities.",
            ]

            deal.ai_summary = (
                "The property shows promise, but additional research "
                "is recommended before making an offer."
            )

        else:
            deal.recommended_actions = [
                "Continue researching before investing additional time."
            ]

            deal.ai_summary = (
                "Current information does not indicate a high-priority acquisition."
            )

        return deal