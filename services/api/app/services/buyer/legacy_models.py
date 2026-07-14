from dataclasses import dataclass, field


@dataclass
class Buyer:
    buyer_name: str
    mailing_address: str | None = None

    city: str | None = None
    state: str | None = None

    purchase_count: int = 0

    average_purchase_price: float = 0.0

    last_purchase_date: str | None = None

    distance_miles: float | None = None

    confidence: float = 0.0

    reasons: list[str] = field(default_factory=list)


@dataclass
class BuyerMatchResult:
    buyers: list[Buyer] = field(default_factory=list)