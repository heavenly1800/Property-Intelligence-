from models import DecisionResult
from rules.market_score import MarketScoreRule


class DecisionEngine:
    def evaluate(self, property_data: dict) -> DecisionResult:
        market = MarketScoreRule().evaluate(property_data)

        return DecisionResult(
            market=market,
            seller=None,
            property=None,
            buyers=None,
            risk=None,
            profit=None,
            recommendation=None,
        )