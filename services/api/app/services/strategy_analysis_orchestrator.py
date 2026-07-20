from app.infrastructure.database.comparable_repository import ComparableRepository
from app.infrastructure.database.property_media_analysis_repository import PropertyMediaAnalysisRepository
from app.infrastructure.database.property_repository import PropertyRepository
from app.infrastructure.database.strategy_analysis_repository import StrategyAnalysisRepository
from app.services.buyer_service import BuyerService
from app.services.strategy_analysis_service import DealStrategyEngine


class StrategyAnalysisOrchestrator:
    @classmethod
    def calculate(cls, property_id: str):
        property_data = PropertyRepository.get(property_id)
        if not property_data: return None
        comparable = ComparableRepository.get_analysis(property_id)
        rehab = PropertyMediaAnalysisRepository.get_summary(property_id)
        try: buyer_demand = BuyerService().get_matches(property_id).market_demand
        except Exception: buyer_demand = "Unknown"
        return StrategyAnalysisRepository.create(DealStrategyEngine.analyze(property_data, comparable, rehab, buyer_demand))

    @classmethod
    def create_once(cls, property_id: str):
        existing = StrategyAnalysisRepository.latest(property_id)
        return existing if existing else cls.calculate(property_id)
