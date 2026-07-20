from datetime import datetime, timezone

from app.core.settings import get_settings


class DealStrategyEngine:
    ASSUMPTIONS_VERSION = "deal-strategy-2026.1"
    STRATEGIES = ("wholesale", "wholetail", "flip", "rental_hold")
    LIMITATIONS = [
        "Deterministic screening analysis only; not lender-grade or investor-grade underwriting.",
        "Taxes, insurance, financing, permits, income taxes, and hidden-condition costs are not modeled unless explicitly stated.",
        "Tax-assessed values are excluded from market value and ARV calculations.",
        "Rental cash flow is unlevered because financing assumptions are outside this slice.",
    ]

    @staticmethod
    def _number(value): return float(value) if isinstance(value, (int, float)) else None

    @classmethod
    def resolve_inputs(cls, property_data: dict, comparable: dict | None, rehab: dict | None, buyer_demand: str = "Unknown") -> dict:
        comparable = comparable or {}; rehab = rehab or {}; units = cls._number(property_data.get("unit_count")) or 1
        acquisition = cls._number(property_data.get("offer_amount"))
        acquisition_basis = "explicit offer amount" if acquisition is not None else "asking price"
        if acquisition is None: acquisition = cls._number(property_data.get("asking_price"))

        if cls._number(comparable.get("estimated_market_value")) is not None:
            current = (cls._number(comparable.get("current_market_value_low")), cls._number(comparable.get("current_market_value_high")))
            current_basis, current_confidence = "comparable-derived current market value", cls._number(comparable.get("comparable_analysis_confidence")) or 0
        else:
            manual = cls._number(property_data.get("estimated_market_value")); current = (manual, manual)
            current_basis, current_confidence = "manual estimated market value", .55 if manual is not None else 0

        if cls._number(comparable.get("estimated_after_repair_value")) is not None:
            arv = (cls._number(comparable.get("after_repair_value_low")), cls._number(comparable.get("after_repair_value_high")))
            arv_basis, arv_confidence = "comparable-derived ARV", cls._number(comparable.get("comparable_analysis_confidence")) or 0
        else:
            manual_low = cls._number(property_data.get("estimated_after_repair_value_low")) or cls._number(property_data.get("after_repair_value"))
            manual_high = cls._number(property_data.get("estimated_after_repair_value_high")) or cls._number(property_data.get("after_repair_value"))
            arv = (manual_low, manual_high); arv_basis, arv_confidence = "manual ARV", .55 if manual_low is not None and manual_high is not None else 0

        manual_rehab = (cls._number(property_data.get("estimated_rehab_cost_low")), cls._number(property_data.get("estimated_rehab_cost_high")))
        if all(value is not None for value in manual_rehab): rehab_range, rehab_basis, rehab_confidence = manual_rehab, "manual rehab range", .8
        else:
            rehab_range = (cls._number(rehab.get("estimated_visible_repair_cost_low")), cls._number(rehab.get("estimated_visible_repair_cost_high")))
            rehab_basis, rehab_confidence = "AI/regional visible-repair range", .6 if all(value is not None for value in rehab_range) else 0

        current_rent = cls._number(property_data.get("current_monthly_rent"))
        if current_rent is None and cls._number(property_data.get("current_monthly_rent_per_unit")) is not None: current_rent = cls._number(property_data["current_monthly_rent_per_unit"]) * units
        if current_rent is not None: rent, rent_basis, rent_confidence = current_rent, "current verified total rent", .85
        elif cls._number(comparable.get("estimated_monthly_market_rent")) is not None: rent, rent_basis, rent_confidence = cls._number(comparable["estimated_monthly_market_rent"]), "comparable-derived total market rent", cls._number(comparable.get("comparable_analysis_confidence")) or 0
        else:
            rent = cls._number(property_data.get("estimated_monthly_rent"))
            if rent is None and cls._number(property_data.get("estimated_monthly_rent_per_unit")) is not None: rent = cls._number(property_data["estimated_monthly_rent_per_unit"]) * units
            rent_basis, rent_confidence = "manual estimated total rent", .55 if rent is not None else 0
        source_values = {"asking_price": cls._number(property_data.get("asking_price")), "explicit_offer_amount": cls._number(property_data.get("offer_amount")), "tax_assessed_value_excluded": cls._number(property_data.get("assessed_total_value")), "comparable_current_value": cls._number(comparable.get("estimated_market_value")), "manual_market_value": cls._number(property_data.get("estimated_market_value")), "comparable_arv": cls._number(comparable.get("estimated_after_repair_value")), "manual_arv": cls._number(property_data.get("after_repair_value")), "manual_rehab_low": manual_rehab[0], "manual_rehab_high": manual_rehab[1], "ai_regional_rehab_low": cls._number(rehab.get("estimated_visible_repair_cost_low")), "ai_regional_rehab_high": cls._number(rehab.get("estimated_visible_repair_cost_high")), "current_total_rent": current_rent, "comparable_market_rent": cls._number(comparable.get("estimated_monthly_market_rent")), "manual_estimated_rent": cls._number(property_data.get("estimated_monthly_rent"))}
        return {"source_values": source_values, "acquisition_price": acquisition, "acquisition_basis": acquisition_basis, "current_value_low": current[0], "current_value_high": current[1], "current_value_basis": current_basis, "current_value_confidence": current_confidence, "arv_low": arv[0], "arv_high": arv[1], "arv_basis": arv_basis, "arv_confidence": arv_confidence, "rehab_low": rehab_range[0], "rehab_high": rehab_range[1], "rehab_basis": rehab_basis, "rehab_confidence": rehab_confidence, "monthly_rent": rent, "rent_basis": rent_basis, "rent_confidence": rent_confidence, "unit_count": int(units), "rent_per_unit": rent / units if rent is not None and units else None, "comparable_status": comparable.get("comparable_analysis_status"), "comparable_analyzed_at": comparable.get("analyzed_at"), "buyer_demand": buyer_demand, "research_quality_score": property_data.get("research_quality_score"), "research_risk_level": property_data.get("research_risk_level"), "parcel_certainty": property_data.get("parcel_certainty"), "utility_confidence": property_data.get("utility_confidence"), "flood_risk_level": property_data.get("flood_risk_level"), "special_flood_hazard_area": property_data.get("special_flood_hazard_area"), "owner_name_present": bool(property_data.get("owner_name")), "last_transfer_date_present": bool(property_data.get("last_transfer_date"))}

    @classmethod
    def common_risks(cls, inputs: dict) -> list[str]:
        risks = []
        if inputs["comparable_status"] != "complete": risks.append("insufficient comparables")
        if inputs["arv_confidence"] < .6: risks.append("weak ARV evidence")
        if inputs["rehab_confidence"] < .7: risks.append("uncertain rehab scope")
        if inputs["utility_confidence"] not in ("high", "medium"): risks.append("utility uncertainty")
        if not inputs["owner_name_present"] or not inputs["last_transfer_date_present"]: risks.append("ownership/transfer limitations")
        if inputs["special_flood_hazard_area"] or str(inputs["flood_risk_level"]).lower() == "high": risks.append("flood risk")
        if inputs["parcel_certainty"] != "high": risks.append("parcel mismatch")
        if str(inputs["buyer_demand"]).lower() == "low": risks.append("low buyer demand")
        if inputs.get("comparable_analyzed_at"):
            try:
                stamp = datetime.fromisoformat(str(inputs["comparable_analyzed_at"]).replace("Z", "+00:00"))
                if (datetime.now(timezone.utc) - stamp).days > 180: risks.append("stale data")
            except (TypeError, ValueError): risks.append("stale data")
        return risks

    @staticmethod
    def blank(strategy: str, inputs: dict) -> dict:
        return {"strategy": strategy, "viable": False, "rank": None, "score": 0, "confidence": 0, "acquisition_price_used": inputs["acquisition_price"], "value_basis": None, "value_low": None, "value_high": None, "rehab_cost_low": inputs["rehab_low"], "rehab_cost_high": inputs["rehab_high"], "holding_costs": None, "closing_costs": None, "selling_costs": None, "projected_revenue_low": None, "projected_revenue_high": None, "projected_profit_low": None, "projected_profit_high": None, "projected_return_percentage_low": None, "projected_return_percentage_high": None, "monthly_cash_flow": None, "annual_cash_flow": None, "cap_rate": None, "major_risks": [], "strengths": [], "missing_inputs": [], "formula_notes": []}

    @classmethod
    def score(cls, result: dict, inputs: dict, profitability: float, evidence: float) -> None:
        research = (cls._number(inputs["research_quality_score"]) or 0) / 100
        research *= {"low": 1, "medium": .75, "high": .5}.get(str(inputs["research_risk_level"]).lower(), .6)
        rehab = inputs["rehab_confidence"]; buyer = {"high": 1, "moderate": .65, "low": .2}.get(str(inputs["buyer_demand"]).lower(), .4)
        missing_penalty = min(25, len(result["missing_inputs"]) * 8)
        risk_penalty = min(15, len(result["major_risks"]) * 2)
        result["score"] = round(max(0, min(100, profitability * 45 + evidence * 20 + research * 10 + rehab * 10 + buyer * 5 - missing_penalty - risk_penalty)), 1)
        result["confidence"] = round(max(0, min(1, evidence * .6 + research * .2 + rehab * .2 - len(result["missing_inputs"]) * .1)), 2)
        result["formula_notes"].append("Score = profitability 45% + evidence 20% + research 10% + rehab certainty 10% + buyer demand 5% − missing/risk penalties.")

    @classmethod
    def wholesale(cls, i, risks):
        s=get_settings(); r=cls.blank("wholesale",i); r["major_risks"]=list(risks)
        value_low,value_high,basis=(i["arv_low"],i["arv_high"],i["arv_basis"]) if i["arv_low"] is not None else (i["current_value_low"],i["current_value_high"],i["current_value_basis"])
        r.update(value_basis=basis,value_low=value_low,value_high=value_high)
        if i["acquisition_price"] is None:r["missing_inputs"].append("acquisition price or explicit offer")
        if value_low is None or value_high is None:r["missing_inputs"].append("current value or ARV evidence")
        if i["rehab_low"] is None or i["rehab_high"] is None:r["missing_inputs"].append("rehab cost range")
        if not r["missing_inputs"]:
            ceiling_low=value_low*s.STRATEGY_WHOLESALE_BUYER_DISCOUNT_PERCENTAGE-i["rehab_high"]
            ceiling_high=value_high*s.STRATEGY_WHOLESALE_BUYER_DISCOUNT_PERCENTAGE-i["rehab_low"]
            mao_low=ceiling_low-s.STRATEGY_WHOLESALE_ASSIGNMENT_FEE_TARGET; mao_high=ceiling_high-s.STRATEGY_WHOLESALE_ASSIGNMENT_FEE_TARGET
            spread_low,spread_high=mao_low-i["acquisition_price"],mao_high-i["acquisition_price"]
            r.update(projected_revenue_low=spread_low,projected_revenue_high=spread_high,projected_profit_low=spread_low,projected_profit_high=spread_high,projected_return_percentage_low=spread_low/i["acquisition_price"] if i["acquisition_price"] else None,projected_return_percentage_high=spread_high/i["acquisition_price"] if i["acquisition_price"] else None)
            r["viable"]=spread_low>=s.STRATEGY_MINIMUM_WHOLESALE_SPREAD
            if not r["viable"]:r["major_risks"].append("thin margin")
            if r["viable"]:r["strengths"].append("Conservative assignment spread meets the configured minimum.")
            r["formula_notes"].append(f"Investor ceiling = value × {s.STRATEGY_WHOLESALE_BUYER_DISCOUNT_PERCENTAGE:.0%} − rehab; MAO = ceiling − {s.STRATEGY_WHOLESALE_ASSIGNMENT_FEE_TARGET:,.0f} target fee; assignment spread = MAO − acquisition.")
            cls.score(r,i,min(1,max(0,spread_low/s.STRATEGY_MINIMUM_WHOLESALE_SPREAD)),max(i["arv_confidence"],i["current_value_confidence"]))
        else: cls.score(r,i,0,0)
        return r

    @classmethod
    def wholetail(cls,i,risks):
        s=get_settings();r=cls.blank("wholetail",i);r["major_risks"]=list(risks);r.update(value_basis=i["current_value_basis"],value_low=i["current_value_low"],value_high=i["current_value_high"],rehab_cost_low=s.STRATEGY_WHOLETAIL_LIGHT_REHAB_ALLOWANCE,rehab_cost_high=s.STRATEGY_WHOLETAIL_LIGHT_REHAB_ALLOWANCE)
        if i["acquisition_price"] is None:r["missing_inputs"].append("acquisition price or explicit offer")
        if i["current_value_low"] is None or i["current_value_high"] is None:r["missing_inputs"].append("current market value evidence")
        if not r["missing_inputs"]:
            purchase_close=i["acquisition_price"]*s.STRATEGY_PURCHASE_CLOSING_COST_PERCENTAGE;holding=s.STRATEGY_MONTHLY_HOLDING_COST_ALLOWANCE*s.STRATEGY_WHOLETAIL_HOLDING_PERIOD_MONTHS
            sell_low=i["current_value_low"]*(s.STRATEGY_RESALE_CLOSING_COST_PERCENTAGE+s.STRATEGY_AGENT_DISPOSITION_PERCENTAGE);sell_high=i["current_value_high"]*(s.STRATEGY_RESALE_CLOSING_COST_PERCENTAGE+s.STRATEGY_AGENT_DISPOSITION_PERCENTAGE)
            profit_low=i["current_value_low"]-i["acquisition_price"]-purchase_close-holding-sell_low-s.STRATEGY_WHOLETAIL_LIGHT_REHAB_ALLOWANCE;profit_high=i["current_value_high"]-i["acquisition_price"]-purchase_close-holding-sell_high-s.STRATEGY_WHOLETAIL_LIGHT_REHAB_ALLOWANCE
            invested=i["acquisition_price"]+purchase_close+holding+s.STRATEGY_WHOLETAIL_LIGHT_REHAB_ALLOWANCE;r.update(holding_costs=holding,closing_costs=purchase_close,selling_costs=sell_high,projected_revenue_low=i["current_value_low"],projected_revenue_high=i["current_value_high"],projected_profit_low=profit_low,projected_profit_high=profit_high,projected_return_percentage_low=profit_low/invested,projected_return_percentage_high=profit_high/invested)
            r["viable"]=profit_low>0
            if not r["viable"]:r["major_risks"].append("thin margin")
            else:r["strengths"].append("Light-rehab resale remains profitable without assuming full ARV.")
            r["formula_notes"].append("Profit = current/lightly-improved resale value − acquisition − light rehab allowance − purchase closing − holding − resale/disposition costs; full ARV is not used.")
            cls.score(r,i,min(1,max(0,profit_low/(invested*.1))),i["current_value_confidence"])
        else:cls.score(r,i,0,0)
        return r

    @classmethod
    def flip(cls,i,risks):
        s=get_settings();r=cls.blank("flip",i);r["major_risks"]=list(risks);r.update(value_basis=i["arv_basis"],value_low=i["arv_low"],value_high=i["arv_high"])
        if i["acquisition_price"] is None:r["missing_inputs"].append("acquisition price or explicit offer")
        if i["arv_low"] is None or i["arv_high"] is None:r["missing_inputs"].append("ARV range")
        if i["rehab_low"] is None or i["rehab_high"] is None:r["missing_inputs"].append("rehab cost range")
        if not r["missing_inputs"]:
            purchase_close=i["acquisition_price"]*s.STRATEGY_PURCHASE_CLOSING_COST_PERCENTAGE;holding=s.STRATEGY_MONTHLY_HOLDING_COST_ALLOWANCE*s.STRATEGY_FLIP_HOLDING_PERIOD_MONTHS
            sale_rate=s.STRATEGY_RESALE_CLOSING_COST_PERCENTAGE+s.STRATEGY_AGENT_DISPOSITION_PERCENTAGE;sell_low=i["arv_low"]*sale_rate;sell_high=i["arv_high"]*sale_rate
            profit_low=i["arv_low"]-i["acquisition_price"]-i["rehab_high"]-purchase_close-holding-sell_low;profit_high=i["arv_high"]-i["acquisition_price"]-i["rehab_low"]-purchase_close-holding-sell_high
            invested_low=i["acquisition_price"]+i["rehab_high"]+purchase_close+holding;r.update(holding_costs=holding,closing_costs=purchase_close,selling_costs=sell_high,projected_revenue_low=i["arv_low"],projected_revenue_high=i["arv_high"],projected_profit_low=profit_low,projected_profit_high=profit_high,projected_return_percentage_low=profit_low/invested_low,projected_return_percentage_high=profit_high/(i["acquisition_price"]+i["rehab_low"]+purchase_close+holding))
            r["viable"]=r["projected_return_percentage_low"]>=s.STRATEGY_MINIMUM_DESIRED_FLIP_MARGIN
            if not r["viable"]:r["major_risks"].append("thin margin")
            else:r["strengths"].append("Conservative flip return meets the configured margin.")
            r["formula_notes"].append("Profit = ARV − acquisition − rehab − purchase closing − holding − resale closing − disposition costs; low case uses low ARV and high rehab.")
            cls.score(r,i,min(1,max(0,r["projected_return_percentage_low"]/s.STRATEGY_MINIMUM_DESIRED_FLIP_MARGIN)),i["arv_confidence"])
        else:cls.score(r,i,0,0)
        return r

    @classmethod
    def rental(cls,i,risks):
        s=get_settings();r=cls.blank("rental_hold",i);r["major_risks"]=list(risks)+["missing financing assumptions"]
        r.update(value_basis=i["rent_basis"],value_low=i["monthly_rent"],value_high=i["monthly_rent"])
        if i["acquisition_price"] is None:r["missing_inputs"].append("acquisition price or explicit offer")
        if i["monthly_rent"] is None:r["missing_inputs"].append("verified, comparable-derived, or manual estimated rent")
        if not r["missing_inputs"]:
            annual_gross=i["monthly_rent"]*12;expense_rate=s.STRATEGY_RENTAL_VACANCY_PERCENTAGE+s.STRATEGY_RENTAL_MANAGEMENT_PERCENTAGE+s.STRATEGY_RENTAL_MAINTENANCE_PERCENTAGE+s.STRATEGY_RENTAL_CAPITAL_RESERVE_PERCENTAGE;noi=annual_gross*(1-expense_rate)
            rehab=i["rehab_high"] or 0;purchase_close=i["acquisition_price"]*s.STRATEGY_PURCHASE_CLOSING_COST_PERCENTAGE;basis=i["acquisition_price"]+rehab+purchase_close;cap=noi/basis if basis else None
            r.update(closing_costs=purchase_close,projected_revenue_low=annual_gross,projected_revenue_high=annual_gross,projected_profit_low=noi,projected_profit_high=noi,annual_cash_flow=noi,monthly_cash_flow=noi/12,cap_rate=cap,projected_return_percentage_low=cap,projected_return_percentage_high=cap)
            r["viable"]=cap is not None and cap>=s.STRATEGY_MINIMUM_DESIRED_RENTAL_CAP_RATE
            if not r["viable"]:r["major_risks"].append("thin margin")
            else:r["strengths"].append(f"Unlevered cap rate meets the configured minimum across {i['unit_count']} unit(s).")
            r["formula_notes"].append(f"Annual gross = total monthly rent × 12 ({i['unit_count']} units; {i['rent_per_unit']:,.0f} per unit when available). NOI = gross × (1 − vacancy − management − maintenance − reserves). Cash flow shown is unlevered NOI; no debt service is assumed.")
            cls.score(r,i,min(1,max(0,cap/s.STRATEGY_MINIMUM_DESIRED_RENTAL_CAP_RATE)),i["rent_confidence"])
        else:cls.score(r,i,0,0)
        return r

    @classmethod
    def analyze(cls, property_data: dict, comparable: dict | None = None, rehab: dict | None = None, buyer_demand: str = "Unknown") -> dict:
        inputs=cls.resolve_inputs(property_data,comparable,rehab,buyer_demand);risks=cls.common_risks(inputs)
        results=[cls.wholesale(inputs,risks),cls.wholetail(inputs,risks),cls.flip(inputs,risks),cls.rental(inputs,risks)]
        viable=sorted((r for r in results if r["viable"]),key=lambda x:x["score"],reverse=True)
        for rank,item in enumerate(viable,1):item["rank"]=rank
        missing=sorted({value for result in results for value in result["missing_inputs"]});recommended=viable[0]["strategy"] if viable else None
        return {"property_id":property_data["property_id"],"recommended_strategy":recommended,"recommendation_confidence":viable[0]["confidence"] if viable else 0,"analysis_status":"complete" if viable else "insufficient_or_nonviable","analyzed_at":datetime.now(timezone.utc).isoformat(),"assumptions_version":cls.ASSUMPTIONS_VERSION,"missing_inputs":missing,"limitations":cls.LIMITATIONS,"recommended_next_action":f"Validate the {recommended.replace('_',' ')} assumptions with current source documents." if recommended else (f"Provide {missing[0].lower()}." if missing else "Review margins and risk evidence before selecting a strategy."),"input_snapshot":inputs,"results":results}
