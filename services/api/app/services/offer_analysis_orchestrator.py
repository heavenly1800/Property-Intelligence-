from app.infrastructure.database.comparable_repository import ComparableRepository
from app.infrastructure.database.offer_analysis_repository import OfferAnalysisRepository
from app.infrastructure.database.property_media_analysis_repository import PropertyMediaAnalysisRepository
from app.infrastructure.database.property_repository import PropertyRepository
from app.infrastructure.database.strategy_analysis_repository import StrategyAnalysisRepository
from app.services.offer_analysis_service import OfferCalculator


class OfferAnalysisOrchestrator:
    @classmethod
    def calculate(cls, property_id: str, selected_strategy: str | None, allow_over_asking_offer: bool = False):
        property_data = PropertyRepository.get(property_id)
        if not property_data: return None
        if selected_strategy is None:
            strategy = StrategyAnalysisRepository.latest(property_id)
            selected_strategy = (strategy or {}).get("recommended_strategy")
        if selected_strategy not in ("wholesale", "wholetail", "flip", "rental_hold"):
            selected_strategy = "wholesale"
        return OfferAnalysisRepository.create(OfferCalculator.calculate(property_data, ComparableRepository.get_analysis(property_id), PropertyMediaAnalysisRepository.get_summary(property_id), selected_strategy, allow_over_asking_offer))

    @classmethod
    def manual(cls, property_id: str, target_offer: float, target_margin: float | None, notes: str | None):
        property_data = PropertyRepository.get(property_id)
        return OfferAnalysisRepository.create(OfferCalculator.manual(property_data, target_offer, target_margin, notes)) if property_data else None
