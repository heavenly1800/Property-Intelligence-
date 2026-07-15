from typing import Any

from .providers.base import ResearchProvider
from .providers.models import (
    ResearchProviderResult,
    ResearchProviderStatus,
    ResearchResult,
)


class ResearchAggregator:
    def __init__(self, providers: list[ResearchProvider]):
        self.providers = providers

    async def execute(self, property_data: dict[str, Any]) -> ResearchResult:
        results: list[ResearchProviderResult] = []
        working_property = dict(property_data)

        for provider in self.providers:
            try:
                provider_result = await provider.execute(working_property)
                results.append(provider_result)

                if provider_result.status == ResearchProviderStatus.COMPLETED:
                    working_property.update(provider_result.data)
            except Exception as error:
                results.append(
                    ResearchProviderResult(
                        provider=provider.__class__.__name__.removesuffix("Provider"),
                        status=ResearchProviderStatus.FAILED,
                        message=str(error),
                    )
                )

        completed = [
            result.provider for result in results
            if result.status == ResearchProviderStatus.COMPLETED
        ]
        failed = [
            result.provider for result in results
            if result.status == ResearchProviderStatus.FAILED
        ]
        confidence_values = [
            result.confidence for result in results
            if result.status == ResearchProviderStatus.COMPLETED
        ]
        terminal = {
            ResearchProviderStatus.COMPLETED,
            ResearchProviderStatus.FAILED,
            ResearchProviderStatus.SKIPPED,
        }

        return ResearchResult(
            providers=results,
            completed_providers=completed,
            failed_providers=failed,
            progress=round(100 * sum(result.status in terminal for result in results) / len(results)) if results else 0,
            completed=bool(results) and all(result.status in terminal for result in results),
            confidence=round(sum(confidence_values) / len(confidence_values), 2) if confidence_values else 0.0,
        )
