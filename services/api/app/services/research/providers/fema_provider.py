from typing import Any

from .base import ResearchProvider
from .models import ResearchProviderResult, ResearchProviderStatus


class FEMAProvider(ResearchProvider):
    async def execute(self, property_data: dict[str, Any]) -> ResearchProviderResult:
        return ResearchProviderResult(
            provider="FEMA",
            status=ResearchProviderStatus.SKIPPED,
            message="FEMA data integration has not been configured.",
        )
