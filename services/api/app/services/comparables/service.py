from __future__ import annotations

from .models import ComparableResult, ComparableSale


class ComparableService:
    """
    Comparable Sales Intelligence.

    Placeholder implementation.

    Future providers may include:

    - Zillow
    - Realtor
    - ATTOM
    - DataTree
    - MLS
    - Land.com
    """

    @staticmethod
    def evaluate(
        property_data: dict,
    ) -> ComparableResult:

        #
        # Placeholder values.
        #
        # Later these will come from real
        # comparable-sale providers.
        #

        comparables = [
            ComparableSale(
                address="101 Main St",
                sale_price=45000,
                acres=1.1,
                distance_miles=0.4,
            ),
            ComparableSale(
                address="214 Oak Ave",
                sale_price=47000,
                acres=1.0,
                distance_miles=0.8,
            ),
            ComparableSale(
                address="88 Pine Rd",
                sale_price=43000,
                acres=0.9,
                distance_miles=0.7,
            ),
        ]

        estimated_value = (
            sum(
                c.sale_price
                for c in comparables
            )
            / len(comparables)
        )

        average_price_per_acre = (
            sum(
                c.sale_price / c.acres
                for c in comparables
                if c.acres
            )
            / len(comparables)
        )

        return ComparableResult(
            estimated_value=round(
                estimated_value,
                2,
            ),
            average_price_per_acre=round(
                average_price_per_acre,
                2,
            ),
            confidence=72,
            comparables=comparables,
        )