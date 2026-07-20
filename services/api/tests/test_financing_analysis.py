import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.services.financing_analysis_service import FinancingAnalysisService

RESOLVED={"acquisition_price":600000.0,"acquisition_basis":"asking price","current_value_low":700000.0,"current_value_high":700000.0,"current_value_basis":"comparable current value","current_value_confidence":.8,"arv_low":850000.0,"arv_high":850000.0,"arv_basis":"comparable ARV","arv_confidence":.8,"rehab_low":50000.0,"rehab_high":70000.0,"rehab_basis":"manual rehab range","rehab_confidence":.8,"monthly_rent":9000.0,"rent_basis":"current verified total rent","rent_confidence":.85,"source_values":{"tax_assessed_value_excluded":999999}}
BASE={"financing_scenario_id":"s1","scenario_name":"Base","financing_type":"conventional","purchase_price":None,"down_payment_amount":None,"down_payment_percentage":.25,"loan_amount":None,"interest_rate":.07,"amortization_years":30,"loan_term_months":360,"interest_only_months":0,"points_percentage":.01,"origination_fee":1000,"appraisal_fee":500,"lender_fee":500,"other_financing_costs":0,"balloon_payment_month":None,"prepayment_penalty":0,"closing_costs_financed":False,"rehab_financed_amount":0,"reserve_requirement":25000,"notes":None,"is_approved":True}

class FinancingAnalysisTest(unittest.TestCase):
    def analyze(self,**changes): return FinancingAnalysisService.analyze({**BASE,**changes},RESOLVED,{"recommended_offer":570000.0})
    def test_amortizing_formula_and_offer_precedence(self):
        result=self.analyze(); principal=427500; rate=.07/12
        self.assertAlmostEqual(result["monthly_principal_interest"],principal*rate*(1+rate)**360/((1+rate)**360-1),6)
        self.assertEqual(result["input_snapshot"]["purchase_price_basis"],"current recommended offer")
    def test_explicit_scenario_purchase_precedes_offer(self): self.assertEqual(self.analyze(purchase_price=555000)["input_snapshot"]["purchase_price"],555000)
    def test_interest_only_and_payment_shock(self):
        result=self.analyze(interest_only_months=24)
        self.assertAlmostEqual(result["monthly_interest_only"],427500*.07/12)
        self.assertEqual(result["annual_debt_service"],result["monthly_interest_only"]*12)
        self.assertTrue(any("payment shock" in x for x in result["warnings"]))
    def test_cash_scenario(self):
        result=self.analyze(financing_type="cash",interest_rate=None,amortization_years=None,loan_term_months=None,points_percentage=0)
        self.assertEqual(result["annual_debt_service"],0); self.assertIsNone(result["debt_service_coverage_ratio"])
        self.assertAlmostEqual(result["leveraged_annual_cash_flow"],result["input_snapshot"]["annual_noi"])
    def test_dscr_cash_flow_coc_and_break_even(self):
        result=self.analyze(); noi=result["input_snapshot"]["annual_noi"]
        self.assertAlmostEqual(result["debt_service_coverage_ratio"],noi/result["annual_debt_service"])
        self.assertAlmostEqual(result["leveraged_annual_cash_flow"],noi-result["annual_debt_service"])
        self.assertAlmostEqual(result["cash_on_cash_return"],result["leveraged_annual_cash_flow"]/result["total_cash_required"])
        self.assertGreater(result["break_even_occupancy"],0)
    def test_ltv_ltc_rehab_financing_and_arv(self):
        result=self.analyze(financing_type="hard_money",loan_amount=500000,rehab_financed_amount=40000)
        self.assertAlmostEqual(result["loan_to_value"],500000/850000); self.assertGreater(result["financed_basis"],500000)
        self.assertEqual(result["input_snapshot"]["value"],850000)
    def test_balloon_balance_and_interest(self):
        result=self.analyze(loan_term_months=60,balloon_payment_month=60)
        self.assertGreater(result["balloon_balance"],0); self.assertGreater(result["total_interest_over_term"],0)
        self.assertTrue(any("Balloon risk" in x for x in result["warnings"]))
    def test_multifamily_total_rent_and_tax_exclusion(self):
        result=self.analyze(); self.assertEqual(result["input_snapshot"]["monthly_rent"],9000)
        self.assertNotEqual(result["input_snapshot"]["value"],result["input_snapshot"]["tax_assessed_value_excluded"])
    def test_six_stress_cases(self):
        cases={x["case"]:x for x in self.analyze()["stress_tests"]}; self.assertEqual(len(cases),6)
        self.assertLess(cases["rate +1%"]["debt_service_coverage_ratio"],cases["base"]["debt_service_coverage_ratio"])
        self.assertLess(cases["combined"]["cash_on_cash_return"],cases["base"]["cash_on_cash_return"])
    def test_missing_inputs_reduce_confidence(self):
        weak={**RESOLVED,"monthly_rent":None,"current_value_low":None,"current_value_high":None}
        result=FinancingAnalysisService.analyze(BASE,weak,None)
        self.assertIn("current or comparable-derived rent",result["missing_inputs"]); self.assertLess(result["analysis_confidence"],.8)
    def test_routes_registered(self):
        paths=set(app.openapi()["paths"]); required={"/properties/{property_id}/financing-scenarios","/properties/{property_id}/financing-scenarios/{scenario_id}","/properties/{property_id}/financing-scenarios/{scenario_id}/analyze","/properties/{property_id}/financing-analysis","/properties/{property_id}/financing-analysis/history"}
        self.assertTrue(required.issubset(paths))
    def test_create_patch_and_history_api_contracts(self):
        client=TestClient(app); payload={"scenario_name":"Cash","financing_type":"cash"}
        with patch("app.routers.financing.FinancingRepository.create_scenario",return_value={"financing_scenario_id":"s1",**payload}): self.assertEqual(client.post("/properties/PROP-001/financing-scenarios",json=payload).status_code,200)
        with patch("app.routers.financing.FinancingRepository.update_scenario",return_value={"financing_scenario_id":"s1","scenario_name":"Edited"}): self.assertEqual(client.patch("/properties/PROP-001/financing-scenarios/s1",json={"scenario_name":"Edited"}).status_code,200)
        with patch("app.routers.financing.FinancingRepository.history",return_value=[{"financing_analysis_id":"a1"}]): self.assertEqual(len(client.get("/properties/PROP-001/financing-analysis/history").json()),1)

if __name__=="__main__": unittest.main()
