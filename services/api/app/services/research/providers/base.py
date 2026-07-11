from abc import ABC, abstractmethod
from typing import Any


class ResearchProvider(ABC):
    """
    Base class for all research providers.

    Every provider accepts a property (or property identifier)
    and returns a normalized dictionary of research results.
    """

    @abstractmethod
    async def research(self, property_data: dict[str, Any]) -> dict[str, Any]:
        """
        Execute research against an external provider.

        Returns only the fields this provider can supply.
        """
        raise NotImplementedError