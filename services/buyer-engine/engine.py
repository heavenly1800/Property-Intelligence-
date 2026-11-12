from models import BuyerMatchResult


class BuyerEngine:
    """
    Finds and ranks potential cash buyers for a property.
    """

    def find_buyers(self, property_data: dict) -> BuyerMatchResult:
        # No verified buyer provider or repository is connected yet.
        return BuyerMatchResult()
