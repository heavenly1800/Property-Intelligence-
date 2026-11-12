import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.services.decision_service import DecisionService
from app.services.opportunity_service import OpportunityService
from app.services.property_service import PropertyService


class OpportunityEvaluationTest(unittest.TestCase):
    def test_missing_data_is_not_assigned_a_default_score(self):
        result = OpportunityService.analyze({"property_id": "empty"})
        self.assertIsNone(result.score)
        self.assertIsNone(result.confidence)
        self.assertIsNone(result.strategy)
        self.assertEqual(result.evaluation_status, "not_evaluated")
        self.assertIn("research", result.next_action.lower())

    def test_partial_data_is_not_presented_as_confident(self):
        result = OpportunityService.analyze(
            {"property_id": "partial", "property_type": "Vacant Land"}
        )
        self.assertIsNone(result.score)
        self.assertIsNone(result.confidence)

    def test_populated_record_defers_to_deal_strategy_analysis(self):
        result = OpportunityService.analyze(
            {
                "property_id": "populated",
                "property_type": "Vacant Land",
                "research_quality_score": 85,
                "asking_price": 100000,
                "after_repair_value": 180000,
            }
        )
        self.assertIsNone(result.score)
        self.assertIsNone(result.confidence)
        self.assertIn("Deal Strategy", result.next_action)

    def test_property_list_exposes_nullable_compatibility_fields(self):
        with patch(
            "app.services.property_service.PropertyRepository.get_all",
            return_value=[{"property_id": "p1", "address": "1 Main St"}],
        ):
            result = PropertyService.get_all()[0]

        self.assertIsNone(result["opportunity_score"])
        self.assertIsNone(result["confidence"])
        self.assertEqual(result["opportunity_evaluation_status"], "not_evaluated")


class DecisionEvaluationTest(unittest.TestCase):
    def test_missing_data_returns_not_evaluated_instead_of_zero(self):
        with patch(
            "app.services.decision_service.PropertyRepository.get",
            return_value={"property_id": "empty"},
        ):
            result = DecisionService.evaluate("empty")

        self.assertIsNone(result.score)
        self.assertIsNone(result.confidence)
        self.assertEqual(result.evaluation_status, "not_evaluated")

    def test_partial_legacy_signals_do_not_create_a_score(self):
        with patch(
            "app.services.decision_service.PropertyRepository.get",
            return_value={"property_id": "partial", "years_owned": 20},
        ):
            result = DecisionService.evaluate("partial")

        self.assertIsNone(result.score)
        self.assertIsNone(result.confidence)

    def test_decision_api_preserves_nullable_score_contract(self):
        with patch(
            "app.services.decision_service.PropertyRepository.get",
            return_value={"property_id": "p1", "research_quality_score": 80},
        ):
            response = TestClient(app).get("/decision/p1")

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json()["score"])
        self.assertIsNone(response.json()["confidence"])
        self.assertEqual(response.json()["evaluation_status"], "not_evaluated")


if __name__ == "__main__":
    unittest.main()
