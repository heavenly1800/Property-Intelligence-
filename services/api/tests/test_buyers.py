import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.services.buyer.engine import BuyerEngine
from app.services.buyer_service import BuyerService


class BuyerDiscoveryTest(unittest.TestCase):
    def test_engine_returns_no_unverified_or_sample_buyers(self):
        self.assertEqual(BuyerEngine().find_buyers({"property_id": "p1"}), [])

    def test_service_returns_explicit_empty_verified_result(self):
        with patch(
            "app.services.buyer_service.PropertyRepository.get",
            return_value={"property_id": "p1"},
        ):
            result = BuyerService().find_buyers("p1")

        self.assertIsNotNone(result)
        self.assertEqual(result.buyers, [])
        self.assertEqual(result.status, "no_verified_buyers")
        self.assertEqual(result.message, "No verified buyers found.")
        self.assertIsNone(result.average_confidence)
        self.assertEqual(result.market_demand, "Unknown")

    def test_service_distinguishes_missing_property(self):
        with patch(
            "app.services.buyer_service.PropertyRepository.get",
            return_value=None,
        ):
            self.assertIsNone(BuyerService().find_buyers("missing"))

    def test_api_contract_returns_empty_result_and_not_an_error(self):
        client = TestClient(app)
        with patch(
            "app.services.buyer_service.PropertyRepository.get",
            return_value={"property_id": "p1"},
        ):
            response = client.get("/buyers/p1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["buyers"], [])
        self.assertEqual(response.json()["status"], "no_verified_buyers")

    def test_api_returns_not_found_for_inaccessible_or_missing_property(self):
        client = TestClient(app)
        with patch(
            "app.services.buyer_service.PropertyRepository.get",
            return_value=None,
        ):
            response = client.get("/buyers/missing")

        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
