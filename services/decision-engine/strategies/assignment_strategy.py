from dataclasses import dataclass, field


@dataclass
class StrategyEvaluation:
    score: float | None = None
    confidence: float | None = None
    evaluation_status: str = "not_evaluated"

    estimated_offer: float | None = None
    estimated_assignment_fee: float | None = None

    reasons: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)

    next_action: str = ""


class AssignmentStrategy:

    def evaluate(self, property_data: dict) -> StrategyEvaluation:
        evaluation = StrategyEvaluation()
        if property_data.get("research_quality_score") is None:
            evaluation.next_action = "Complete property research before making a decision."
        else:
            evaluation.next_action = "Run Deal Strategy analysis using verified value, repair, and rent evidence."

        return evaluation
