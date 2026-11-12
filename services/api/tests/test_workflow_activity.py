import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.services.crm_service import CrmService


class PersistedWorkflowActivityTest(unittest.TestCase):
    def test_offer_history_endpoint_returns_persisted_analysis_status(self):
        saved = [
            {
                "offer_analysis_id": "a1",
                "property_id": "p1",
                "offer_status": "calculated",
                "recommended_offer": 125000,
            }
        ]
        with patch(
            "app.routers.offer_analysis.OfferAnalysisRepository.history",
            return_value=saved,
        ):
            response = TestClient(app).get("/properties/p1/offer-history")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["offer_status"], "calculated")

    def test_sent_offer_endpoint_returns_persisted_activity(self):
        sent = [
            {
                "sent_offer_id": "s1",
                "property_id": "p1",
                "offer_amount": 125000,
                "status": "sent",
            }
        ]
        with patch("app.routers.crm.CrmRepository.list", return_value=sent):
            response = TestClient(app).get("/properties/p1/sent-offers")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["status"], "sent")

    def test_recording_sent_offer_persists_activity_without_faking_crm_stage(self):
        payload = {"offer_analysis_id": "a1", "offer_amount": 125000, "status": "sent"}
        saved = {"sent_offer_id": "s1", "property_id": "p1", **payload}
        with (
            patch("app.services.crm_service.CrmRepository.create", return_value=saved) as create,
            patch("app.services.crm_service.CrmRepository.activity") as activity,
            patch("app.services.crm_service.PropertyRepository.update") as update_property,
        ):
            result = CrmService.record_sent_offer("p1", payload)

        self.assertEqual(result["sent_offer_id"], "s1")
        create.assert_called_once()
        activity.assert_called_once()
        update_property.assert_not_called()


if __name__ == "__main__":
    unittest.main()
