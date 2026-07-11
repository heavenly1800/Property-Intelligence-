from typing import Any

from .providers.base import ResearchProvider
from .providers.models import ResearchResult


class ResearchOrchestrator:
    def __init__(self, providers: list[ResearchProvider]):
        self.providers = providers

    async def run(
        self,
        property_data: dict[str, Any],
    ) -> ResearchResult:
        result = ResearchResult()

        provider_status: dict[str, str] = {}

        for provider in self.providers:
            provider_name = provider.__class__.__name__

            try:
                provider_result = await provider.research(property_data)

                status = provider_result.pop(
                    "research_status",
                    "Success",
                )

                provider_status[provider_name] = status

                for key, value in provider_result.items():
                    setattr(result, key, value)

            except Exception as e:
                provider_status[provider_name] = f"Failed: {e}"

        result.provider_status = provider_status

        return result