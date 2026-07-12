from typing import Any

from .base import ResearchProvider
from .models import ResearchProviderResult, ResearchProviderStatus


class TaxAssessorProvider(ResearchProvider):
    async def execute(self, property_data: dict[str, Any]) -> ResearchProviderResult:
        return ResearchProviderResult(
            provider="Tax Assessor",
            status=ResearchProviderStatus.SKIPPED,
            message="Tax assessor integration has not been configured.",
        )
