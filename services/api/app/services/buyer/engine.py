from .models import BuyerMatch


class BuyerEngine:
    """
    Finds and ranks potential cash buyers for a property.
    """

    def find_buyers(self, property_data: dict) -> list[BuyerMatch]:
        """Return only buyers backed by a verified data source.

        No buyer provider or persisted buyer repository exists yet, so there
        are no verified records to return.
        """
        return []
