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

        deal.recommended_actions = [
            "Use the evidence-based Deal Strategy analysis."
        ]
        deal.ai_summary = "Legacy deal scoring is not evaluated."

        return deal
