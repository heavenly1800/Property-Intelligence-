import unittest
from unittest.mock import AsyncMock, patch

from app.services.repair_cost_service import RepairCostService
from app.services.vision_analysis_service import PropertyConditionAnalysisService


PROFILES = [
    {"profile_id": "city", "profile_name": "Twentynine Palms", "state": "CA", "county": "San Bernardino", "city": "Twentynine Palms", "zip_code": "92277", "effective_date": "2026-07-01", "confidence": .65, "is_default": False},
    {"profile_id": "national", "profile_name": "National", "effective_date": "2026-07-01", "confidence": .45, "is_default": True},
]
ITEMS = [
    {"category": "flooring", "unit_type": "square foot", "cost_low_per_unit": 4, "cost_high_per_unit": 10, "minimum_job_cost_low": 500, "minimum_job_cost_high": 1000, "labor_material_notes": "Underwriting allowance", "contingency_percentage": 0},
    {"category": "general contingency", "unit_type": "percentage contingency", "cost_low_per_unit": 0, "cost_high_per_unit": 0, "minimum_job_cost_low": 0, "minimum_job_cost_high": 0, "labor_material_notes": "Contingency", "contingency_percentage": 15},
]


class RegionalRepairCostEngineTest(unittest.IsolatedAsyncioTestCase):
    def test_exact_city_match(self):
        profile, confidence, reason = RepairCostService.select_profile({"city": "Twentynine Palms", "zip_code": "92277", "county": "San Bernardino", "state": "CA"}, PROFILES)
        self.assertEqual(profile["profile_id"], "city"); self.assertEqual(confidence, 1); self.assertEqual(reason, "exact city/zip match")

    def test_county_fallback(self):
        profile, confidence, reason = RepairCostService.select_profile({"city": "Joshua Tree", "zip_code": "92252", "county": "San Bernardino", "state": "CA"}, PROFILES)
        self.assertEqual(profile["profile_id"], "city"); self.assertEqual(confidence, .85); self.assertEqual(reason, "county match")

    def test_national_fallback(self):
        profile, confidence, reason = RepairCostService.select_profile({"city": "Reno", "state": "NV"}, PROFILES)
        self.assertEqual(profile["profile_id"], "national"); self.assertEqual(confidence, .4); self.assertEqual(reason, "default national fallback")

    def test_minimum_job_cost_for_unknown_quantity(self):
        result = RepairCostService.price_analysis([{"category": "flooring", "description": "Visible damage", "area": "room"}], {}, PROFILES, ITEMS)
        self.assertEqual(result["items"][0]["extended_cost_low"], 500); self.assertEqual(result["items"][0]["extended_cost_high"], 1000)
        self.assertTrue(result["items"][0]["minimum_job_cost_applied"])

    def test_quantity_estimate_and_contingency(self):
        item = {"category": "flooring", "description": "Replace floor", "area": "room", "estimated_quantity_low": 200, "estimated_quantity_high": 300, "quantity_unit": "square foot", "quantity_confidence": .6}
        result = RepairCostService.price_analysis([item], {}, PROFILES, ITEMS)
        self.assertEqual(result["visible_repair_subtotal_low"], 800); self.assertEqual(result["visible_repair_subtotal_high"], 3000)
        self.assertEqual(result["contingency_low"], 120); self.assertEqual(result["contingency_high"], 450)
        self.assertEqual(result["total_low"], 920); self.assertEqual(result["total_high"], 3450)

    async def test_aggregation_deduplicates_and_does_not_overwrite_manual_rehab(self):
        repair = {"category": "flooring", "area": "kitchen", "description": "Replace damaged floor", "extended_cost_low": 800, "extended_cost_high": 2000}
        base = {"condition_rating": "fair", "rent_ready_status": "minor_work", "analyzed_at": "2026-07-01T00:00:00Z", "analysis_confidence": .7, "estimated_repair_items": [repair], "observed_issues": [], "unknown_inspection_items": [], "regional_profile_id": "city", "regional_profile_name": "Twentynine Palms", "profile_match_confidence": 1, "profile_match_reason": "exact city/zip match", "cost_assumption_effective_date": "2026-07-01", "cost_limitations": [], "visible_repair_subtotal_low": 800, "visible_repair_subtotal_high": 2000, "contingency_low": 120, "contingency_high": 300}
        with patch("app.services.vision_analysis_service.PropertyMediaAnalysisRepository.list_for_property", return_value=[{**base, "media_id": "one"}, {**base, "media_id": "two"}]), patch("app.services.vision_analysis_service.PropertyMediaAnalysisRepository.upsert_summary", side_effect=lambda value: value) as save, patch("app.services.vision_analysis_service.PropertyRepository.update") as property_update:
            result = await PropertyConditionAnalysisService.aggregate("PROP-001")
        self.assertEqual(result["visible_repair_subtotal_low"], 800); self.assertEqual(len(result["visible_repair_items"]), 1)
        property_update.assert_not_called(); save.assert_called_once()


if __name__ == "__main__": unittest.main()
