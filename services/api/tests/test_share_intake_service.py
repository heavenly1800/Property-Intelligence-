import unittest
from unittest.mock import patch

from app.services.share_intake_service import ShareIntakeService


class ShareIntakeServiceTest(unittest.TestCase):
  def test_process_matches_prop_001_and_analyzes_explicit_text(self):
    share = {
        "share_id": "00000000-0000-0000-0000-000000000001",
        "status": "pending",
        "source_url": "https://www.zillow.com/homedetails/123-Main-St/",
        "source_domain": "zillow.com",
        "shared_text": "123 Main St offered at $250,000 with 3 bed and 2 bath.",
        "title": None,
        "notes": None,
    }
    completed = {**share, "status": "completed", "matched_property_id": "PROP-001"}

    with (
        patch("app.services.share_intake_service.ShareIntakeRepository.get", return_value=share),
        patch("app.services.share_intake_service.ShareIntakeRepository.update", side_effect=[share, completed]) as update_share,
        patch("app.services.share_intake_service.PropertyRepository.find_by_address", return_value={"property_id": "PROP-001"}),
        patch("app.services.share_intake_service.PropertyRepository.create") as create_property,
        patch("app.services.share_intake_service.PropertyRepository.update") as update_property,
    ):
        result = ShareIntakeService.process(share["share_id"])

    self.assertEqual(result["matched_property_id"], "PROP-001")
    create_property.assert_not_called()
    property_id, fields = update_property.call_args.args
    self.assertEqual(property_id, "PROP-001")
    self.assertEqual(fields["listing_url"], share["source_url"])
    self.assertEqual(fields["listing_raw_text"], share["shared_text"])
    self.assertEqual(fields["asking_price"], 250000)
    self.assertEqual(fields["bedrooms"], 3)
    self.assertEqual(update_share.call_args.args[1]["detected_address"], "123 Main St")


if __name__ == "__main__":
    unittest.main()
