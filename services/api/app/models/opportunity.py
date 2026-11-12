from dataclasses import dataclass


@dataclass
class Opportunity:

    property_id: str

    score: int | None

    strategy: str | None

    confidence: int | None

    next_action: str

    evaluation_status: str
