import sys
from pathlib import Path

from app.infrastructure.database.property_repository import PropertyRepository

buyer_engine_path = (
    Path(__file__).resolve().parents[3] / "buyer-engine"
)

if str(buyer_engine_path) not in sys.path:
    sys.path.append(str(buyer_engine_path))

from engine import BuyerEngine  # noqa: E402


class BuyerService:
    @staticmethod
    def find_buyers(property_id: str):
        property_data = PropertyRepository.get(property_id)

        if not property_data:
            return None

        engine = BuyerEngine()

        return engine.find_buyers(property_data)