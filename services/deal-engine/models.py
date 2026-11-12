from dataclasses import dataclass, field


@dataclass
class DealScore:

    overall_score: float | None = None

    confidence: float | None = None

    market_value: float | None = None

    recommended_offer: float | None = None

    assignment_fee: float | None = None

    strategy: str = ""

    priority: str = "Not evaluated"

    strengths: list[str] = field(default_factory=list)

    risks: list[str] = field(default_factory=list)

    missing_information: list[str] = field(default_factory=list)

    recommended_actions: list[str] = field(default_factory=list)

    ai_summary: str = ""
