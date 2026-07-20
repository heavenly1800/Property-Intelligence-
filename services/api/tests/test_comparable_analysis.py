import unittest
from datetime import date

from app.services.comparables.service import ComparableAnalysisService


TODAY = date(2026, 7, 19)
SUBJECT = {"property_id": "PROP-001", "property_type": "multifamily", "property_subtype": "fourplex", "unit_count": 4, "bedrooms": 8, "bathrooms": 4, "square_feet": 4000, "acres": .4, "year_built": 1985, "property_condition": "fair", "estimated_market_value": 123, "after_repair_value": 456, "estimated_monthly_rent": 789}


def comp(index: int, kind="sale", **values):
    base = {"comparable_id": f"c-{kind}-{index}", "comparable_type": kind, "source_name": "County records" if kind == "sale" else "Owner listing", "source_url": f"https://example.test/{kind}/{index}", "source_record_id": f"{kind}-{index}", "address": f"{index} Desert Rd", "distance_miles": 2 + index / 10, "property_type": "multifamily", "property_subtype": "fourplex", "unit_count": 4, "bedrooms": 8, "bathrooms": 4, "square_feet": 4000, "lot_acres": .4, "year_built": 1985, "condition": "fair", "included": True}
    if kind == "sale": base.update({"sale_price": 400000 + index * 10000, "sale_date": "2026-05-01"})
    else: base.update({"monthly_rent": 6000 + index * 100, "listing_date": "2026-06-01"})
    return {**base, **values}


class ComparableAnalysisTest(unittest.TestCase):
    def test_fourplex_scores_higher_than_unit_mismatch(self):
        exact, _ = ComparableAnalysisService.score(SUBJECT, comp(1), TODAY)
        mismatch, _ = ComparableAnalysisService.score(SUBJECT, comp(2, unit_count=2, property_subtype="duplex"), TODAY)
        self.assertGreater(exact, mismatch)

    def test_single_family_is_explicitly_excluded_for_fourplex(self):
        item = comp(1, property_type="single family", property_subtype="detached", unit_count=1)
        self.assertIn("multifamily", ComparableAnalysisService.exclusion_reason(SUBJECT, item, set(), TODAY))

    def test_distance_and_recency_reduce_score_and_weight(self):
        close = comp(1, distance_miles=1, sale_date="2026-07-01")
        far = comp(2, distance_miles=15, sale_date="2025-01-01")
        close["match_score"] = ComparableAnalysisService.score(SUBJECT, close, TODAY)[0]
        far["match_score"] = ComparableAnalysisService.score(SUBJECT, far, TODAY)[0]
        self.assertGreater(close["match_score"], far["match_score"])
        self.assertGreater(ComparableAnalysisService.weight(SUBJECT, close, TODAY), ComparableAnalysisService.weight(SUBJECT, far, TODAY))

    def test_stale_comparable_is_excluded(self):
        item = comp(1, sale_date="2020-01-01")
        self.assertEqual(ComparableAnalysisService.exclusion_reason(SUBJECT, item, set(), TODAY), "stale sale/listing date")

    def test_insufficient_comparables_produce_no_estimate(self):
        _, analysis = ComparableAnalysisService.analyze(SUBJECT, [comp(1), comp(1, "rental")], TODAY)
        self.assertIsNone(analysis["estimated_market_value"]); self.assertIsNone(analysis["estimated_monthly_market_rent"])
        self.assertEqual(analysis["comparable_analysis_status"], "insufficient_evidence")

    def test_weighted_sale_and_rental_estimates(self):
        items = [comp(i, sale_price=value) for i, value in enumerate((400000, 420000, 440000), 1)] + [comp(i, "rental", monthly_rent=value) for i, value in enumerate((6000, 6200, 6400), 1)]
        _, analysis = ComparableAnalysisService.analyze(SUBJECT, items, TODAY)
        self.assertGreater(analysis["estimated_market_value"], 400000); self.assertLess(analysis["estimated_market_value"], 440000)
        self.assertGreater(analysis["estimated_monthly_market_rent"], 6000); self.assertLess(analysis["estimated_monthly_market_rent"], 6400)

    def test_arv_requires_and_uses_renovated_sales(self):
        sales = [comp(i, sale_price=value, condition="renovated") for i, value in enumerate((500000, 520000, 540000), 1)]
        rentals = [comp(i, "rental") for i in range(1, 4)]
        _, analysis = ComparableAnalysisService.analyze(SUBJECT, sales + rentals, TODAY)
        self.assertGreater(analysis["estimated_after_repair_value"], 500000); self.assertLess(analysis["estimated_after_repair_value"], 540000)

    def test_duplicate_and_outlier_exclusion(self):
        duplicate = comp(2, source_record_id="sale-1")
        items = [comp(1, sale_price=400000), duplicate, comp(3, sale_price=410000), comp(4, sale_price=1200000)]
        scored, _ = ComparableAnalysisService.analyze(SUBJECT, items, TODAY)
        self.assertEqual(scored[1]["exclusion_reason"], "duplicate source record")
        self.assertEqual(scored[3]["exclusion_reason"], "outlier sale price")

    def test_prop_001_fourplex_manual_vertical_slice_does_not_overwrite_manual_values(self):
        manual_before = {key: SUBJECT[key] for key in ("estimated_market_value", "after_repair_value", "estimated_monthly_rent")}
        sales = [comp(i, sale_price=420000 + i * 10000, condition="renovated") for i in range(1, 4)]
        rentals = [comp(i, "rental", monthly_rent=6100 + i * 100) for i in range(1, 4)]
        scored, analysis = ComparableAnalysisService.analyze(SUBJECT, sales + rentals, TODAY)
        self.assertEqual(len([x for x in scored if x["included"]]), 6)
        self.assertEqual(analysis["comparable_analysis_status"], "complete")
        self.assertEqual(manual_before, {key: SUBJECT[key] for key in manual_before})


if __name__ == "__main__": unittest.main()
