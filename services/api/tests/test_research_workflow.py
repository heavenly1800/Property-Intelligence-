import unittest
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app
from app.services.research.providers.models import (
    ResearchProviderResult,
    ResearchProviderStatus,
    ResearchResult,
)
from app.services.research.service import ResearchService


class ResearchWorkflowTest(unittest.IsolatedAsyncioTestCase):
    async def test_persists_only_non_null_completed_provider_findings(self):
        result = ResearchResult(
            providers=[
                ResearchProviderResult(
                    provider="Census",
                    status=ResearchProviderStatus.COMPLETED,
                    data={"latitude": 34.1, "longitude": None, "county": ""},
                    confidence=1,
                ),
                ResearchProviderResult(
                    provider="FEMA",
                    status=ResearchProviderStatus.FAILED,
                    data={"flood_zone": None},
                    message="Unavailable",
                ),
            ],
            completed_providers=["Census"],
            failed_providers=["FEMA"],
            progress=100,
            completed=True,
            confidence=1,
        )
        updates = []

        with (
            patch(
                "app.services.research.service.PropertyRepository.get",
                return_value={
                    "property_id": "p1",
                    "address": "1 Main St",
                    "longitude": -117.2,
                    "flood_zone": "X",
                },
            ),
            patch(
                "app.services.research.service.ResearchAggregator.execute",
                new=AsyncMock(return_value=result),
            ),
            patch(
                "app.services.research.service.PropertyRepository.update",
                side_effect=lambda _, data: updates.append(data),
            ),
        ):
            response = await ResearchService.run("p1")

        self.assertEqual(updates[0], {"latitude": 34.1})
        self.assertNotIn("longitude", updates[0])
        self.assertNotIn("flood_zone", updates[0])
        self.assertIsNotNone(response.quality_summary)

    async def test_missing_property_does_not_run_providers_or_write(self):
        with (
            patch(
                "app.services.research.service.PropertyRepository.get",
                return_value=None,
            ),
            patch(
                "app.services.research.service.ResearchAggregator.execute",
                new=AsyncMock(),
            ) as execute,
            patch(
                "app.services.research.service.PropertyRepository.update"
            ) as update,
        ):
            self.assertIsNone(await ResearchService.run("missing"))

        execute.assert_not_awaited()
        update.assert_not_called()


class ResearchRouterTest(unittest.TestCase):
    def test_registered_post_endpoint_returns_research_schema(self):
        result = ResearchResult(
            providers=[
                ResearchProviderResult(
                    provider="Census",
                    status=ResearchProviderStatus.SKIPPED,
                    message="Address unavailable.",
                )
            ],
            progress=100,
            completed=True,
        )
        with patch(
            "app.routers.research.ResearchService.run",
            new=AsyncMock(return_value=result),
        ):
            response = TestClient(app).post("/research/p1/run")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["providers"][0]["status"], "skipped")
        self.assertEqual(response.json()["quality_summary"], None)

    def test_old_endpoint_is_not_registered(self):
        response = TestClient(app).post("/research/p1")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
