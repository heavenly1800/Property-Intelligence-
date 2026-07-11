from models import Buyer, BuyerMatchResult


class BuyerEngine:
    """
    Finds and ranks potential cash buyers for a property.
    """

    def find_buyers(self, property_data: dict) -> BuyerMatchResult:
        result = BuyerMatchResult()

        # Temporary placeholder.
        # Real county transfer record providers will populate this.
        result.buyers.append(
            Buyer(
                buyer_name="Sample Investment LLC",
                purchase_count=12,
                confidence=75,
                reasons=[
                    "Purchased multiple vacant land parcels.",
                    "Active in the same county.",
                ],
            )
        )

        return result