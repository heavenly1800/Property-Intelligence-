from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Provider(ABC):
    """
    Base class for every Property Intelligence provider.

    Providers expose ONE responsibility:

        fetch()

    They retrieve authoritative data from an
    external source and return normalized data.

    Providers never:

    - score properties
    - make decisions
    - calculate offers
    - perform workflow logic

    Those belong to the Intelligence Layer.
    """

    name: str = "provider"

    version: str = "1.0"

    source: str = "Unknown"

    @abstractmethod
    def fetch(
        self,
        property_data: dict,
    ) -> Any:
        """
        Fetch normalized data for a property.
        """
        raise NotImplementedError