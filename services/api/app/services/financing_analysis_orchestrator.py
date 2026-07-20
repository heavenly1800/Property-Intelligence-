from app.infrastructure.database.comparable_repository import ComparableRepository
from app.infrastructure.database.financing_repository import FinancingRepository
from app.infrastructure.database.offer_analysis_repository import OfferAnalysisRepository
from app.infrastructure.database.property_media_analysis_repository import PropertyMediaAnalysisRepository
from app.infrastructure.database.property_repository import PropertyRepository
from app.services.financing_analysis_service import FinancingAnalysisService
from app.services.strategy_analysis_service import DealStrategyEngine

class FinancingAnalysisOrchestrator:
    @classmethod
    def analyze(cls, property_id, scenario_id):
        scenario = FinancingRepository.get_scenario(property_id, scenario_id)
        property_data = PropertyRepository.get(property_id)
        if not scenario or not property_data: return None
        resolved = DealStrategyEngine.resolve_inputs(property_data, ComparableRepository.get_analysis(property_id), PropertyMediaAnalysisRepository.get_summary(property_id))
        result = FinancingAnalysisService.analyze(scenario, resolved, OfferAnalysisRepository.latest(property_id))
        return FinancingRepository.create_analysis({**result, "property_id": property_id, "financing_scenario_id": scenario_id})
