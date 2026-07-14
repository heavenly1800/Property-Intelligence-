from __future__ import annotations

from abc import ABC, abstractmethod

from app.services.comparables.models import ComparableResult


class ComparableProvider(ABC):
    """
    Base class for comparable-sale providers.

    Future implementations:

    - RentCast
    - ATTOM
    - DataTree
    - MLS
    """

    @abstractmethod
    def search(
        self,
        property_data: dict,
    ) -> ComparableResult:
        """
        Return comparable sales for a property.
        """
        raise NotImplementedError