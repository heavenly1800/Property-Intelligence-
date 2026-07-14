from dataclasses import dataclass, field


@dataclass
class ComparableSale:
    address: str
    sale_price: float
    acres: float | None = None
    square_feet: int | None = None
    distance_miles: float | None = None


@dataclass
class ComparableResult:
    estimated_value: float
    average_price_per_acre: float | None = None
    confidence: int = 0

    comparables: list[ComparableSale] = field(
        default_factory=list
    )