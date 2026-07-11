from app.infrastructure.database.property_repository import PropertyRepository
from app.services.research.orchestrator import ResearchOrchestrator
from app.services.research.providers.census_provider import CensusProvider


class ResearchService:
    @staticmethod
    async def run(property_id: str):
        property_data = PropertyRepository.get(property_id)

        if not property_data:
            return None

        orchestrator = ResearchOrchestrator(
            providers=[
                CensusProvider(),
            ]
        )

        result = await orchestrator.run(property_data)

        PropertyRepository.update(
            property_id,
            {
                "address": result.address or property_data["address"],
                "latitude": result.latitude,
                "longitude": result.longitude,
            },
        )

        return PropertyRepository.get(property_id)