from models import DecisionScore


class MarketScoreRule:
    def evaluate(self, property_data: dict) -> DecisionScore:
        score = DecisionScore(
            name="Market",
            score=50,
        )

        score.reasons.append(
            "Base market score."
        )

        return scores