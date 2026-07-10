from dataclasses import dataclass


@dataclass
class Opportunity:

    property_id: str

    score: int

    strategy: str

    confidence: int

    next_action: str