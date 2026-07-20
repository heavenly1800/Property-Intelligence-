import math
from datetime import datetime, timezone

from app.core.settings import get_settings
from app.services.strategy_analysis_service import DealStrategyEngine


class OfferCalculator:
    ASSUMPTIONS_VERSION = "offer-calculator-2026.1"
    LIMITATIONS = ["Screening estimate only; not a contract, offer letter, appraisal, legal opinion, or financing commitment.", "Title, taxes, insurance, financing, permits, inspection findings, and transaction-specific terms require separate verification.", "Tax-assessed value is excluded from all offer formulas."]

    @staticmethod
    def _round_down(value: float) -> float:
        increment = get_settings().OFFER_ROUNDING_INCREMENT
        return max(0, math.floor(value / increment) * increment)

    @classmethod
    def _range(cls, mao: float) -> tuple[float, float, float]:
        buffer = get_settings().OFFER_NEGOTIATION_BUFFER_PERCENTAGE
        high = cls._round_down(mao); recommended = min(high, cls._round_down(high * (1 - buffer))); low = min(recommended, cls._round_down(high * (1 - 2 * buffer)))
        return low, recommended, high

    @classmethod
    def warnings(cls, inputs: dict, strategy: str) -> list[str]:
        warnings = []
        if max(inputs["arv_confidence"], inputs["current_value_confidence"]) < .6: warnings.append("weak comparable confidence")
        if str(inputs["research_risk_level"]).lower() == "high": warnings.append("high research risk")
        if not inputs["owner_name_present"] or not inputs["last_transfer_date_present"]: warnings.append("missing ownership/title verification")
        if strategy == "rental_hold": warnings.append("missing financing assumptions")
        if "stale data" in DealStrategyEngine.common_risks(inputs): warnings.append("stale data")
        return warnings

    @classmethod
    def calculate(cls, property_data: dict, comparable: dict | None, rehab: dict | None, strategy: str, allow_over_asking_offer: bool = False) -> dict:
        inputs = DealStrategyEngine.resolve_inputs(property_data, comparable, rehab)
        s = get_settings(); blockers = []; notes = []; mao = None; metric_label = None; metric_low = metric_high = None
        value_basis = inputs["arv_basis"] if strategy in ("wholesale", "flip") else inputs["current_value_basis"]
        value_low = inputs["arv_low"] if strategy in ("wholesale", "flip") else inputs["current_value_low"]
        value_high = inputs["arv_high"] if strategy in ("wholesale", "flip") else inputs["current_value_high"]
        rehab_low, rehab_high = inputs["rehab_low"], inputs["rehab_high"]

        if strategy == "wholesale":
            if value_low is None or value_high is None:
                value_low, value_high, value_basis = inputs["current_value_low"], inputs["current_value_high"], inputs["current_value_basis"]
            if value_low is None or value_high is None: blockers.append("insufficient ARV evidence and insufficient current-value evidence")
            if rehab_low is None or rehab_high is None: blockers.append("unknown rehab")
            if not blockers:
                spread = max(s.OFFER_ASSIGNMENT_FEE_TARGET, s.OFFER_DESIRED_WHOLESALE_SPREAD)
                ceiling_low = value_low * s.OFFER_WHOLESALE_BUYER_DISCOUNT_PERCENTAGE - rehab_high
                ceiling_high = value_high * s.OFFER_WHOLESALE_BUYER_DISCOUNT_PERCENTAGE - rehab_low
                mao = min(ceiling_low, ceiling_high) - spread; metric_label = "assignment spread"
                notes.append(f"Investor ceiling = value × {s.OFFER_WHOLESALE_BUYER_DISCOUNT_PERCENTAGE:.0%} − rehab; MAO = conservative ceiling − max(assignment target, desired spread).")
        elif strategy == "flip":
            if value_low is None or value_high is None: blockers.append("insufficient ARV evidence")
            if rehab_low is None or rehab_high is None: blockers.append("unknown rehab")
            if not blockers:
                sale_rate = s.OFFER_RESALE_CLOSING_COST_PERCENTAGE + s.OFFER_DISPOSITION_AGENT_PERCENTAGE
                net_low = value_low * (1 - sale_rate) - rehab_high - s.OFFER_HOLDING_COST_ALLOWANCE
                dollar_constraint = (net_low - s.OFFER_MINIMUM_FLIP_PROFIT_DOLLARS) / (1 + s.OFFER_PURCHASE_CLOSING_COST_PERCENTAGE)
                pct = s.OFFER_DESIRED_FLIP_PROFIT_PERCENTAGE
                percentage_constraint = (net_low - pct * (rehab_high + s.OFFER_HOLDING_COST_ALLOWANCE)) / ((1 + s.OFFER_PURCHASE_CLOSING_COST_PERCENTAGE) * (1 + pct))
                mao = min(dollar_constraint, percentage_constraint); metric_label = "projected flip profit"
                notes.append("Flip MAO is the lower of the minimum-dollar-profit constraint and target-return constraint after rehab, purchase closing, holding, resale closing, and disposition costs.")
        elif strategy == "wholetail":
            rehab_low = rehab_high = s.OFFER_WHOLETAIL_LIGHT_REHAB_ALLOWANCE
            if value_low is None or value_high is None: blockers.append("insufficient current-value evidence")
            if not blockers:
                sale_rate = s.OFFER_RESALE_CLOSING_COST_PERCENTAGE + s.OFFER_DISPOSITION_AGENT_PERCENTAGE; margin = s.OFFER_WHOLETAIL_TARGET_MARGIN
                net = value_low * (1 - sale_rate) - rehab_high - s.OFFER_HOLDING_COST_ALLOWANCE
                mao = (net - margin * (rehab_high + s.OFFER_HOLDING_COST_ALLOWANCE)) / ((1 + s.OFFER_PURCHASE_CLOSING_COST_PERCENTAGE) * (1 + margin)); metric_label = "projected wholetail profit"
                notes.append("Wholetail MAO uses current/lightly-improved value—not ARV—and preserves the target margin after light rehab, holding, purchase/resale closing, and disposition costs.")
        elif strategy == "rental_hold":
            if inputs["monthly_rent"] is None: blockers.append("insufficient rental evidence")
            if rehab_low is None or rehab_high is None: blockers.append("unknown rehab")
            if not blockers:
                expense_rate = s.OFFER_RENTAL_VACANCY_PERCENTAGE + s.OFFER_RENTAL_MANAGEMENT_PERCENTAGE + s.OFFER_RENTAL_MAINTENANCE_PERCENTAGE + s.OFFER_RENTAL_RESERVE_PERCENTAGE
                noi = inputs["monthly_rent"] * 12 * (1 - expense_rate); maximum_basis = noi / s.OFFER_RENTAL_MINIMUM_CAP_RATE
                mao = (maximum_basis - rehab_high) / (1 + s.OFFER_PURCHASE_CLOSING_COST_PERCENTAGE); metric_label = "unlevered cap rate"
                notes.append(f"NOI = total monthly rent × 12 × (1 − vacancy − management − maintenance − reserves); maximum basis = NOI ÷ {s.OFFER_RENTAL_MINIMUM_CAP_RATE:.1%}; offer ceiling removes rehab and purchase closing costs. Financing is not modeled. {inputs['unit_count']} unit(s), {inputs['rent_per_unit']:,.0f} rent per unit.")
        else: blockers.append("custom offers must use the manual endpoint")

        if mao is not None and mao <= 0: blockers.append("thin margin")
        warnings = cls.warnings(inputs, strategy); strengths = []; low = recommended = high = None
        if not blockers and mao is not None:
            offer_ceiling = mao
            asking = DealStrategyEngine._number(property_data.get("asking_price"))
            if asking is not None and asking < mao and not allow_over_asking_offer:
                offer_ceiling = asking
                strengths.append("Asking price is below the calculated investment ceiling.")
            low, recommended, high = cls._range(offer_ceiling)
            if strategy == "wholesale":
                conservative_ceiling = value_low * s.OFFER_WHOLESALE_BUYER_DISCOUNT_PERCENTAGE - rehab_high
                metric_low = metric_high = conservative_ceiling - recommended
            elif strategy in ("flip", "wholetail"):
                sale_rate = s.OFFER_RESALE_CLOSING_COST_PERCENTAGE + s.OFFER_DISPOSITION_AGENT_PERCENTAGE
                metric_low = value_low * (1-sale_rate) - recommended*(1+s.OFFER_PURCHASE_CLOSING_COST_PERCENTAGE) - rehab_high - s.OFFER_HOLDING_COST_ALLOWANCE
                metric_high = value_high * (1-sale_rate) - recommended*(1+s.OFFER_PURCHASE_CLOSING_COST_PERCENTAGE) - rehab_low - s.OFFER_HOLDING_COST_ALLOWANCE
            else:
                expense_rate = s.OFFER_RENTAL_VACANCY_PERCENTAGE+s.OFFER_RENTAL_MANAGEMENT_PERCENTAGE+s.OFFER_RENTAL_MAINTENANCE_PERCENTAGE+s.OFFER_RENTAL_RESERVE_PERCENTAGE
                noi=inputs["monthly_rent"]*12*(1-expense_rate); metric_low=metric_high=noi/(recommended*(1+s.OFFER_PURCHASE_CLOSING_COST_PERCENTAGE)+rehab_high)
        asking = DealStrategyEngine._number(property_data.get("asking_price")); discount = max(0, (asking-recommended)/asking) if asking and recommended is not None else None
        margin_to_mao = (mao-recommended)/mao if mao and recommended is not None else None
        evidence = inputs["rent_confidence"] if strategy == "rental_hold" else (inputs["current_value_confidence"] if strategy == "wholetail" else max(inputs["arv_confidence"], inputs["current_value_confidence"]))
        confidence = max(0, min(1, evidence*.7 + inputs["rehab_confidence"]*.3 - len(blockers)*.15 - len(warnings)*.03))
        inputs["allow_over_asking_offer"] = allow_over_asking_offer
        return {"property_id": property_data["property_id"], "selected_strategy": strategy, "offer_status": "calculated" if not blockers else "blocked", "recommended_offer_low": low, "recommended_offer": recommended, "recommended_offer_high": high, "maximum_allowable_offer": cls._round_down(mao) if mao is not None and mao > 0 else None, "seller_asking_price": asking, "estimated_discount_to_asking": discount, "offer_confidence": round(confidence,2), "value_basis": value_basis, "rehab_basis": inputs["rehab_basis"], "rent_basis": inputs["rent_basis"], "assumptions_version": cls.ASSUMPTIONS_VERSION, "input_snapshot": inputs, "blockers": blockers, "warnings": warnings, "strengths": strengths, "missing_inputs": list(blockers), "limitations": cls.LIMITATIONS, "formula_notes": notes + [f"Offer range uses a {s.OFFER_NEGOTIATION_BUFFER_PERCENTAGE:.0%} negotiation buffer and rounds down to {s.OFFER_ROUNDING_INCREMENT:,.0f}. Economic MAO is preserved; offers are capped at asking unless over-asking is explicitly allowed."], "projected_metric_label": metric_label, "projected_metric_low": metric_low, "projected_metric_high": metric_high, "margin_to_mao": margin_to_mao, "allow_over_asking_offer": allow_over_asking_offer, "created_at": datetime.now(timezone.utc).isoformat()}

    @classmethod
    def manual(cls, property_data: dict, target_offer: float, target_margin: float | None, notes: str | None) -> dict:
        return {"property_id": property_data["property_id"], "selected_strategy": "custom", "offer_status": "manual", "recommended_offer_low": target_offer, "recommended_offer": target_offer, "recommended_offer_high": target_offer, "maximum_allowable_offer": None, "seller_asking_price": DealStrategyEngine._number(property_data.get("asking_price")), "estimated_discount_to_asking": (property_data["asking_price"]-target_offer)/property_data["asking_price"] if property_data.get("asking_price") else None, "offer_confidence": 1, "value_basis": "manual target", "rehab_basis": None, "rent_basis": None, "assumptions_version": cls.ASSUMPTIONS_VERSION, "input_snapshot": {"manual_target_offer": target_offer, "manual_target_margin": target_margin, "tax_assessed_value_excluded": property_data.get("assessed_total_value")}, "blockers": [], "warnings": ["Manual offer was not validated against calculated strategy constraints."], "missing_inputs": [], "limitations": cls.LIMITATIONS, "formula_notes": ["User-entered custom offer; no calculated offer analysis was altered."], "projected_metric_label": "manual target margin", "projected_metric_low": target_margin, "projected_metric_high": target_margin, "manual_target_margin": target_margin, "manual_notes": notes, "created_at": datetime.now(timezone.utc).isoformat()}
