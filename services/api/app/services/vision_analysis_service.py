from abc import ABC, abstractmethod


class VisionAnalysisService(ABC):
    """Future AI vision contract; no provider is invoked in this release."""

    @abstractmethod
    async def analyze(self, media: dict) -> dict:
        raise NotImplementedError


class PendingVisionAnalysisService(VisionAnalysisService):
    async def analyze(self, media: dict) -> dict:
        return {"analysis_status": "pending", "review_status": "pending_review"}
