import unittest
from unittest.mock import patch

from app.services.offer_analysis_orchestrator import OfferAnalysisOrchestrator
from app.services.offer_analysis_service import OfferCalculator


PROPERTY = {"property_id":"PROP-001","asking_price":300000,"unit_count":4,"estimated_market_value":350000,"after_repair_value":450000,"estimated_rehab_cost_low":30000,"estimated_rehab_cost_high":50000,"estimated_monthly_rent":5600,"research_risk_level":"low","parcel_certainty":"high","utility_confidence":"high","owner_name":"Owner","last_transfer_date":"2025-01-01","assessed_total_value":999999}
COMPARABLE = {"estimated_market_value":380000,"current_market_value_low":360000,"current_market_value_high":400000,"estimated_after_repair_value":500000,"after_repair_value_low":480000,"after_repair_value_high":520000,"estimated_monthly_market_rent":6000,"comparable_analysis_confidence":.85,"comparable_analysis_status":"complete"}
REHAB = {"estimated_visible_repair_cost_low":80000,"estimated_visible_repair_cost_high":100000}


class OfferCalculatorTest(unittest.TestCase):
    def calculate(self,strategy,property_data=None,comparable=COMPARABLE,rehab=REHAB): return OfferCalculator.calculate(property_data or dict(PROPERTY),comparable,rehab,strategy)

    def test_wholesale_mao_and_assignment_spread(self):
        result=self.calculate("wholesale")
        self.assertEqual(result["maximum_allowable_offer"],271000)
        self.assertGreaterEqual(result["projected_metric_low"],15000)
        self.assertEqual(result["projected_metric_label"],"assignment spread")

    def test_flip_preserves_dollar_and_percentage_margins(self):
        result=self.calculate("flip");self.assertEqual(result["offer_status"],"calculated")
        self.assertLessEqual(result["maximum_allowable_offer"],(480000*.92-50000-15000-30000)/1.02)
        self.assertGreaterEqual(result["projected_metric_low"],30000)

    def test_wholetail_uses_current_value_and_target_margin(self):
        result=self.calculate("wholetail")
        self.assertEqual(result["value_basis"],"comparable-derived current market value")
        self.assertEqual(result["input_snapshot"]["arv_low"],480000)
        self.assertGreater(result["projected_metric_low"],0)

    def test_rental_cap_rate_ceiling(self):
        result=self.calculate("rental_hold")
        self.assertEqual(result["projected_metric_label"],"unlevered cap rate")
        self.assertGreaterEqual(result["projected_metric_low"],.06)

    def test_prop_001_multifamily_rent_and_flip(self):
        rental=self.calculate("rental_hold");flip=self.calculate("flip")
        self.assertEqual(rental["input_snapshot"]["unit_count"],4);self.assertEqual(rental["input_snapshot"]["rent_per_unit"],1500)
        self.assertEqual(flip["value_basis"],"comparable-derived ARV")

    def test_manual_rehab_precedence(self):
        result=self.calculate("flip")
        self.assertEqual(result["rehab_basis"],"manual rehab range");self.assertEqual(result["input_snapshot"]["rehab_high"],50000)

    def test_comparable_arv_precedence(self):
        result=self.calculate("flip")
        self.assertEqual(result["input_snapshot"]["arv_low"],480000);self.assertNotEqual(result["input_snapshot"]["arv_low"],PROPERTY["after_repair_value"])

    def test_tax_assessment_is_excluded(self):
        prop={"property_id":"tax","asking_price":100000,"assessed_total_value":900000,"unit_count":1}
        result=OfferCalculator.calculate(prop,None,None,"flip")
        self.assertIn("insufficient ARV evidence",result["blockers"]);self.assertEqual(result["input_snapshot"]["source_values"]["tax_assessed_value_excluded"],900000)

    def test_negotiation_buffer_and_rounding(self):
        result=self.calculate("wholesale")
        self.assertEqual(result["recommended_offer_low"]%1000,0);self.assertEqual(result["recommended_offer"]%1000,0);self.assertEqual(result["recommended_offer_high"]%1000,0)
        self.assertLess(result["recommended_offer_low"],result["recommended_offer"]);self.assertLess(result["recommended_offer"],result["recommended_offer_high"])

    def test_insufficient_inputs_block_calculation(self):
        result=OfferCalculator.calculate({"property_id":"empty","asking_price":1},None,None,"rental_hold")
        self.assertEqual(result["offer_status"],"blocked");self.assertIsNone(result["recommended_offer"]);self.assertIn("insufficient rental evidence",result["blockers"])

    def test_recommended_never_exceeds_mao(self):
        for strategy in ("wholesale","wholetail","flip","rental_hold"):
            result=self.calculate(strategy)
            self.assertLessEqual(result["recommended_offer"],result["maximum_allowable_offer"])

    def test_mao_above_asking_preserves_economic_ceiling_and_caps_offers(self):
        result=self.calculate("wholesale",{**PROPERTY,"asking_price":200000})
        self.assertEqual(result["maximum_allowable_offer"],271000)
        self.assertLessEqual(result["recommended_offer_low"],200000)
        self.assertLessEqual(result["recommended_offer"],200000)
        self.assertLessEqual(result["recommended_offer_high"],200000)
        self.assertIn("Asking price is below the calculated investment ceiling.",result["strengths"])
        self.assertGreater(result["margin_to_mao"],0)

    def test_discount_to_asking_is_never_negative(self):
        result=self.calculate("wholesale",{**PROPERTY,"asking_price":200000},comparable=COMPARABLE,rehab=REHAB)
        self.assertGreaterEqual(result["estimated_discount_to_asking"],0)

    def test_explicit_over_asking_override_uses_mao_range(self):
        result=OfferCalculator.calculate({**PROPERTY,"asking_price":200000},COMPARABLE,REHAB,"wholesale",allow_over_asking_offer=True)
        self.assertGreater(result["recommended_offer"],200000)
        self.assertEqual(result["recommended_offer_high"],result["maximum_allowable_offer"])
        self.assertEqual(result["estimated_discount_to_asking"],0)
        self.assertTrue(result["allow_over_asking_offer"])

    def test_recalculation_is_append_only(self):
        saved=[]
        with patch("app.services.offer_analysis_orchestrator.PropertyRepository.get",return_value=PROPERTY),patch("app.services.offer_analysis_orchestrator.ComparableRepository.get_analysis",return_value=COMPARABLE),patch("app.services.offer_analysis_orchestrator.PropertyMediaAnalysisRepository.get_summary",return_value=REHAB),patch("app.services.offer_analysis_orchestrator.OfferAnalysisRepository.create",side_effect=lambda value:saved.append(value) or {"offer_analysis_id":str(len(saved)),**value}):
            first=OfferAnalysisOrchestrator.calculate("PROP-001","flip");second=OfferAnalysisOrchestrator.calculate("PROP-001","flip")
        self.assertEqual(len(saved),2);self.assertNotEqual(first["offer_analysis_id"],second["offer_analysis_id"])

    def test_manual_offer_is_separate_from_calculated_offer(self):
        calculated=self.calculate("flip");manual=OfferCalculator.manual(PROPERTY,222000,.12,"Seller requested quick close")
        self.assertEqual(manual["selected_strategy"],"custom");self.assertEqual(manual["offer_status"],"manual");self.assertEqual(manual["recommended_offer"],222000)
        self.assertEqual(calculated["selected_strategy"],"flip");self.assertNotEqual(calculated["recommended_offer"],manual["recommended_offer"])


if __name__=="__main__":unittest.main()
