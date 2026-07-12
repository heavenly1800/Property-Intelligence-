from abc import ABC, abstractmethod
from typing import Any

from .models import ResearchProviderResult


class ResearchProvider(ABC):
    """
    Base class for all research providers.

    Every provider accepts a property and returns its own normalized result.
    """

    @abstractmethod
    async def execute(
        self, property_data: dict[str, Any]
    ) -> ResearchProviderResult:
        raise NotImplementedError
