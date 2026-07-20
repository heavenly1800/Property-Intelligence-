import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from app.schemas.photo_analysis import PhotoConditionOutput
from app.services.repair_cost_service import RepairCostService
from app.services.vision_analysis_service import PropertyConditionAnalysisService, VisionAnalysisService


class MockAnalyzer:
    model = "mock-vision-model"

    async def analyze(self, media):
        return {
            "room_or_area": "exterior",
            "visible_condition_summary": "Peeling paint is visible on the south wall.",
            "condition_rating": "fair",
            "observed_issues": [{
                "category": "paint", "description": "Peeling exterior paint", "severity": "moderate",
                "visible_evidence": "Flaking coating is visible", "recommended_action": "Prepare and repaint",
                "confidence": 0.94,
            }],
            "inferred_issues": [],
            "unknown_inspection_items": [{"category": "lead", "description": "Lead content", "reason": "Requires testing"}],
            "estimated_repair_items": [{"category": "paint", "description": "Prepare and repaint visible wall", "area": "exterior", "scope_units": 1}],
            "rent_ready_status": "minor_work", "safety_concerns": [], "analysis_confidence": 0.9,
            "limitations": ["Single exterior photo; no physical inspection."],
        }


class PhotoConditionAnalysisTest(unittest.IsolatedAsyncioTestCase):
    async def test_openai_structured_response_is_mocked(self):
        parsed = PhotoConditionOutput.model_validate(await MockAnalyzer().analyze({}))
        client = MagicMock()
        client.responses.parse = AsyncMock(return_value=SimpleNamespace(output_parsed=parsed))
        storage = MagicMock()
        storage.from_.return_value.download.return_value = b"\xff\xd8\xffmock-image"
        with patch("app.services.vision_analysis_service.supabase", SimpleNamespace(storage=storage)):
            result = await VisionAnalysisService(client=client).analyze({"storage_path": "PROP-001/exterior.jpg", "media_type": "image/jpeg"})
        self.assertEqual(result["condition_rating"], "fair")
        call = client.responses.parse.call_args.kwargs
        self.assertEqual(call["text_format"], PhotoConditionOutput)
        self.assertTrue(call["input"][0]["content"][1]["image_url"].startswith("data:image/jpeg;base64,"))

    async def test_mocked_analysis_uses_deterministic_costs(self):
        media = {"media_id": "media-1", "property_id": "PROP-001", "media_type": "image/jpeg", "storage_path": "PROP-001/exterior.jpg"}
        saved = {}

        def capture(record):
            saved.update(record)
            return {"analysis_id": "analysis-1", **record}

        with (
            patch("app.services.vision_analysis_service.PropertyMediaRepository.get", return_value=media),
            patch("app.services.vision_analysis_service.PropertyMediaRepository.begin_analysis", return_value=media),
            patch("app.services.vision_analysis_service.PropertyMediaRepository.update"),
            patch("app.services.vision_analysis_service.PropertyMediaAnalysisRepository.get", return_value=None),
            patch("app.services.vision_analysis_service.PropertyMediaAnalysisRepository.upsert", side_effect=capture),
            patch("app.services.vision_analysis_service.PropertyRepository.get", return_value={"city": "Twentynine Palms", "zip_code": "92277"}),
            patch.object(RepairCostService, "price_analysis", return_value={
                "items": [{"category": "exterior paint", "description": "Prepare and repaint visible wall", "area": "exterior", "estimated_cost_low": 1500, "estimated_cost_high": 3600}],
                "visible_repair_subtotal_low": 1500, "visible_repair_subtotal_high": 3600,
                "contingency_low": 225, "contingency_high": 540, "total_low": 1725, "total_high": 4140,
                "profile": {"profile_id": "regional", "profile_name": "Twentynine Palms"},
                "profile_match_confidence": 1, "profile_match_reason": "exact city/zip match",
                "cost_assumption_effective_date": "2026-07-01", "cost_limitations": [],
            }),
            patch.object(PropertyConditionAnalysisService, "aggregate", new=AsyncMock(return_value=None)),
        ):
            result = await PropertyConditionAnalysisService.analyze_media("PROP-001", "media-1", reanalyze=True, analyzer=MockAnalyzer())

        self.assertEqual(result["estimated_repair_cost_low"], 1725)
        self.assertEqual(result["estimated_repair_cost_high"], 4140)
        self.assertEqual(saved["raw_analysis"]["estimated_repair_items"][0]["category"], "paint")
        self.assertNotIn("estimated_cost_low", saved["raw_analysis"]["estimated_repair_items"][0])
        self.assertEqual(saved["cost_assumption_version"], RepairCostService.VERSION)

    def test_prompt_prohibits_hidden_condition_certainty(self):
        for condition in ("mold", "asbestos", "lead", "foundation", "internal plumbing", "internal electrical", "HVAC internals", "roof decking", "sewer", "septic"):
            self.assertIn(condition.lower(), VisionAnalysisService.PROMPT.lower())


if __name__ == "__main__":
    unittest.main()
