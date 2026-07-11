from dataclasses import dataclass, field


@dataclass
class StrategyEvaluation:
    score: float = 0.0
    confidence: float = 0.0

    estimated_offer: float | None = None
    estimated_assignment_fee: float | None = None

    reasons: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)

    next_action: str = ""


class AssignmentStrategy:

    def evaluate(self, property_data: dict) -> StrategyEvaluation:
        evaluation = StrategyEvaluation()

        score = 0

        # Long-term ownership
        years_owned = property_data.get("years_owned", 0)
        if years_owned >= 10:
            score += 15
            evaluation.reasons.append(
                "Long-term ownership suggests equity."
            )

        # Utilities
        if property_data.get("utilities_available"):
            score += 15
            evaluation.reasons.append(
                "Utilities are available."
            )

        # Road access
        if property_data.get("legal_access"):
            score += 15
            evaluation.reasons.append(
                "Property has legal access."
            )

        # Flood
        if property_data.get("flood_zone"):
            score -= 20
            evaluation.risks.append(
                "Property is located in a flood zone."
            )

        # Buyer demand
        buyer_demand = property_data.get("buyer_demand", 0)

        score += buyer_demand

        if buyer_demand > 20:
            evaluation.reasons.append(
                "Strong buyer demand."
            )

        score = max(0, min(score, 100))

        evaluation.score = score
        evaluation.confidence = score

        if score >= 80:
            evaluation.next_action = "Call seller immediately."

        elif score >= 60:
            evaluation.next_action = "Complete additional research."

        else:
            evaluation.next_action = "Continue searching."

        return evaluation