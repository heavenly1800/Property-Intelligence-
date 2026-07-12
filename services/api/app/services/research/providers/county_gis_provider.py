from typing import Any

from .base import ResearchProvider
from .models import ResearchProviderResult, ResearchProviderStatus


class CountyGISProvider(ResearchProvider):
    async def execute(self, property_data: dict[str, Any]) -> ResearchProviderResult:
        return ResearchProviderResult(
            provider="County GIS",
            status=ResearchProviderStatus.SKIPPED,
            message="County GIS integration has not been configured.",
        )
