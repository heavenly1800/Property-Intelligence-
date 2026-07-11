from dataclasses import dataclass, field


@dataclass
class DecisionScore:
    name: str
    score: float
    max_score: float = 100.0
    reasons: list[str] = field(default_factory=list)


@dataclass
class StrategyRecommendation:
    strategy: str
    confidence: float
    reasons: list[str]
    risks: list[str]
    next_action: str


@dataclass
class DecisionResult:
    market: DecisionScore
    seller: DecisionScore
    property: DecisionScore
    buyers: DecisionScore
    risk: DecisionScore
    profit: DecisionScore

    recommendation: StrategyRecommendation