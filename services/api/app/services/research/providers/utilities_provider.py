from typing import Any

from .base import ResearchProvider
from .models import ResearchProviderResult, ResearchProviderStatus


class UtilitiesProvider(ResearchProvider):
    async def execute(self, property_data: dict[str, Any]) -> ResearchProviderResult:
        return ResearchProviderResult(
            provider="Utilities",
            status=ResearchProviderStatus.SKIPPED,
            message="Utilities integration has not been configured.",
        )
