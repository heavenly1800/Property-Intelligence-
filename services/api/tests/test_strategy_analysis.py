import unittest
from unittest.mock import patch

from app.services.strategy_analysis_orchestrator import StrategyAnalysisOrchestrator
from app.services.strategy_analysis_service import DealStrategyEngine


PROPERTY = {"property_id": "PROP-001", "asking_price": 200000, "unit_count": 4, "property_type": "multifamily", "property_subtype": "fourplex", "estimated_market_value": 300000, "after_repair_value": 450000, "estimated_rehab_cost_low": 30000, "estimated_rehab_cost_high": 50000, "estimated_monthly_rent": 5600, "research_quality_score": 80, "research_risk_level": "low", "parcel_certainty": "high", "utility_confidence": "high", "flood_risk_level": "low", "special_flood_hazard_area": False, "owner_name": "Owner", "last_transfer_date": "2025-01-01"}
COMPARABLE = {"estimated_market_value": 340000, "current_market_value_low": 320000, "current_market_value_high": 360000, "estimated_after_repair_value": 500000, "after_repair_value_low": 480000, "after_repair_value_high": 520000, "estimated_monthly_market_rent": 6000, "comparable_analysis_confidence": .85, "comparable_analysis_status": "complete"}
REHAB = {"estimated_visible_repair_cost_low": 80000, "estimated_visible_repair_cost_high": 100000}


class DealStrategyEngineTest(unittest.TestCase):
    def analyze(self, property_data=None, comparable=COMPARABLE, rehab=REHAB): return DealStrategyEngine.analyze(property_data or dict(PROPERTY), comparable, rehab, "High")
    @staticmethod
    def result(analysis, name): return next(item for item in analysis["results"] if item["strategy"] == name)

    def test_wholesale_viability_and_mao_formula(self):
        wholesale = self.result(self.analyze(), "wholesale")
        self.assertTrue(wholesale["viable"]); self.assertGreater(wholesale["projected_profit_low"], 10000)
        self.assertIn("MAO", wholesale["formula_notes"][0])

    def test_wholetail_light_rehab_economics(self):
        wholetail = self.result(self.analyze(), "wholetail")
        self.assertEqual(wholetail["rehab_cost_low"], 15000); self.assertEqual(wholetail["rehab_cost_high"], 15000)
        self.assertGreater(wholetail["projected_profit_high"], wholetail["projected_profit_low"])

    def test_flip_low_high_profit(self):
        flip = self.result(self.analyze(), "flip")
        self.assertGreater(flip["projected_profit_high"], flip["projected_profit_low"])
        self.assertEqual(flip["value_basis"], "comparable-derived ARV")

    def test_rental_noi_and_cap_rate_are_unlevered(self):
        rental = self.result(self.analyze(), "rental_hold")
        self.assertAlmostEqual(rental["annual_cash_flow"], 6000 * 12 * .74)
        self.assertAlmostEqual(rental["monthly_cash_flow"], rental["annual_cash_flow"] / 12)
        self.assertGreater(rental["cap_rate"], 0); self.assertIn("unlevered", " ".join(rental["formula_notes"]).lower())

    def test_prop_001_fourplex_rent_is_total_and_per_unit_is_auditable(self):
        analysis = self.analyze(); rental = self.result(analysis, "rental_hold")
        self.assertEqual(analysis["input_snapshot"]["unit_count"], 4); self.assertEqual(analysis["input_snapshot"]["rent_per_unit"], 1500)
        self.assertIn("4 units", rental["formula_notes"][0])

    def test_missing_arv_makes_flip_nonviable(self):
        prop = {**PROPERTY, "after_repair_value": None, "estimated_after_repair_value_low": None, "estimated_after_repair_value_high": None}
        flip = self.result(self.analyze(prop, comparable={"comparable_analysis_status": "insufficient_evidence"}), "flip")
        self.assertFalse(flip["viable"]); self.assertIn("ARV range", flip["missing_inputs"])

    def test_manual_rehab_precedes_ai_regional_rehab(self):
        snapshot = self.analyze()["input_snapshot"]
        self.assertEqual((snapshot["rehab_low"], snapshot["rehab_high"]), (30000, 50000)); self.assertEqual(snapshot["rehab_basis"], "manual rehab range")

    def test_comparable_estimates_precede_manual_estimates(self):
        snapshot = self.analyze()["input_snapshot"]
        self.assertEqual(snapshot["current_value_low"], 320000); self.assertEqual(snapshot["arv_low"], 480000); self.assertEqual(snapshot["monthly_rent"], 6000)

    def test_tax_assessed_value_is_never_a_value_fallback(self):
        prop = {"property_id": "tax-only", "asking_price": 100000, "assessed_total_value": 999999, "unit_count": 1}
        analysis = DealStrategyEngine.analyze(prop, None, None)
        self.assertIsNone(analysis["input_snapshot"]["current_value_low"]); self.assertIsNone(analysis["input_snapshot"]["arv_low"])
        self.assertFalse(self.result(analysis, "flip")["viable"])

    def test_thin_margin_rejects_flip(self):
        prop = {**PROPERTY, "asking_price": 450000}
        flip = self.result(self.analyze(prop), "flip")
        self.assertFalse(flip["viable"]); self.assertIn("thin margin", flip["major_risks"])

    def test_only_viable_strategies_are_ranked(self):
        analysis = self.analyze()
        self.assertTrue(all((item["rank"] is not None) == item["viable"] for item in analysis["results"]))
        ranks = sorted(item["rank"] for item in analysis["results"] if item["viable"])
        self.assertEqual(ranks, list(range(1, len(ranks) + 1)))

    def test_existing_analysis_is_not_overwritten_without_recalculation(self):
        existing = {"strategy_analysis_id": "saved"}
        with patch("app.services.strategy_analysis_orchestrator.StrategyAnalysisRepository.latest", return_value=existing), patch.object(StrategyAnalysisOrchestrator, "calculate") as calculate:
            self.assertIs(StrategyAnalysisOrchestrator.create_once("PROP-001"), existing)
        calculate.assert_not_called()


if __name__ == "__main__": unittest.main()
