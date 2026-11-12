from models import DealScore


class DealScorer:
    """
    Combines all available research into a single investment score.
    """

    def score(self, property_data: dict) -> DealScore:
        deal = DealScore()

        deal.missing_information.append(
            "Legacy Deal Engine scoring is disabled; use Deal Strategy analysis."
        )

        return deal
