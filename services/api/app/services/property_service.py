from app.infrastructure.database.property_repository import PropertyRepository
from app.services.opportunity_service import OpportunityService
from app.services.financial_analysis_service import FinancialAnalysisService


class PropertyService:

    @staticmethod
    def get_all():

        properties = PropertyRepository.get_all()

        for property in properties:

            opportunity = OpportunityService.analyze(property)

            property["opportunity_score"] = opportunity.score
            property["strategy"] = opportunity.strategy
            property["confidence"] = opportunity.confidence
            property["next_action"] = opportunity.next_action

        return properties

    @staticmethod
    def get(property_id: str):
        return PropertyRepository.get(property_id)

    @staticmethod
    def create(data):
        return PropertyRepository.create(data)

    @staticmethod
    def update_financials(property_id: str, data: dict):
        property_data = PropertyRepository.get(property_id)
        if not property_data:
            return None

        merged_data = {**property_data, **data}
        financial_analysis = FinancialAnalysisService.analyze(merged_data)
        PropertyRepository.update(
            property_id,
            {**data, **financial_analysis},
        )
        return PropertyRepository.get(property_id)
