from app.core.settings import get_settings


class FinancingAnalysisService:
    LIMITATIONS = [
        "Screening analysis only; not lender-grade underwriting or a loan quote.",
        "Taxes and insurance are excluded unless already represented in the operating-expense inputs.",
        "Rates, fees, rents, expenses, and values must be independently verified before commitment.",
    ]

    @staticmethod
    def number(value):
        return float(value) if isinstance(value, (int, float)) else None

    @staticmethod
    def payment(principal, annual_rate, months):
        if not principal or not months: return 0.0
        rate = annual_rate / 12
        if rate == 0: return principal / months
        factor = (1 + rate) ** months
        return principal * rate * factor / (factor - 1)

    @classmethod
    def amortization(cls, principal, annual_rate, amortization_months, term_months, io_months, balloon_month):
        if not principal: return 0.0, 0.0
        monthly_rate = annual_rate / 12
        regular = cls.payment(principal, annual_rate, amortization_months)
        balance, interest = principal, 0.0
        payoff_month = min(term_months, balloon_month or term_months)
        for month in range(1, payoff_month + 1):
            charge = balance * monthly_rate
            interest += charge
            if month > io_months:
                balance = max(0.0, balance - max(0.0, regular - charge))
        return balance, interest

    @classmethod
    def analyze(cls, scenario, resolved, offer):
        settings = get_settings(); kind = scenario["financing_type"]
        purchase = cls.number(scenario.get("purchase_price"))
        purchase_basis = "financing scenario purchase price"
        if purchase is None and offer and cls.number(offer.get("recommended_offer")) is not None:
            purchase, purchase_basis = cls.number(offer["recommended_offer"]), "current recommended offer"
        if purchase is None:
            purchase, purchase_basis = resolved["acquisition_price"], resolved["acquisition_basis"]
        rehab = ((resolved.get("rehab_low") or 0) + (resolved.get("rehab_high") or 0)) / 2
        use_arv = kind in ("hard_money", "private") or cls.number(scenario.get("rehab_financed_amount")) > 0
        value_low, value_high = (resolved.get("arv_low"), resolved.get("arv_high")) if use_arv else (resolved.get("current_value_low"), resolved.get("current_value_high"))
        value = (value_low + value_high) / 2 if value_low is not None and value_high is not None else None
        value_basis = resolved.get("arv_basis") if use_arv else resolved.get("current_value_basis")
        rent = resolved.get("monthly_rent")
        missing = []
        if purchase is None: missing.append("purchase price")
        if rent is None: missing.append("current or comparable-derived rent")
        if value is None: missing.append("ARV" if use_arv else "current value")
        rate = cls.number(scenario.get("interest_rate")) or 0
        amort_years = scenario.get("amortization_years")
        term = scenario.get("loan_term_months")
        down = cls.number(scenario.get("down_payment_amount"))
        if down is None and purchase is not None: down = purchase * (cls.number(scenario.get("down_payment_percentage")) or 0)
        down = down or 0
        loan = 0.0 if kind == "cash" else cls.number(scenario.get("loan_amount"))
        if loan is None and purchase is not None: loan = max(0, purchase - down)
        if kind != "cash":
            if scenario.get("interest_rate") is None: missing.append("interest rate")
            if not amort_years and not scenario.get("interest_only_months"): missing.append("amortization years")
            if not term: missing.append("loan term months")
        amort_months = (amort_years or 30) * 12; term = term or amort_months
        io_months = min(scenario.get("interest_only_months") or 0, term)
        monthly_pi = cls.payment(loan, rate, amort_months)
        monthly_io = loan * rate / 12
        active_debt = monthly_io if io_months else monthly_pi
        annual_debt = active_debt * 12
        purchase_closing = (purchase or 0) * settings.STRATEGY_PURCHASE_CLOSING_COST_PERCENTAGE
        fees = loan * (cls.number(scenario.get("points_percentage")) or 0) + sum(cls.number(scenario.get(k)) or 0 for k in ("origination_fee", "appraisal_fee", "lender_fee", "other_financing_costs"))
        rehab_financed = min(rehab, cls.number(scenario.get("rehab_financed_amount")) or 0)
        financed_basis = loan + rehab_financed + (purchase_closing if scenario.get("closing_costs_financed") else 0)
        cash_required = down + fees + max(0, rehab - rehab_financed) + (0 if scenario.get("closing_costs_financed") else purchase_closing) + (cls.number(scenario.get("reserve_requirement")) or 0)
        if kind == "cash": cash_required += max(0, (purchase or 0) - down)
        total_cost = (purchase or 0) + rehab + purchase_closing + fees
        expense_rate = settings.STRATEGY_RENTAL_VACANCY_PERCENTAGE + settings.STRATEGY_RENTAL_MANAGEMENT_PERCENTAGE + settings.STRATEGY_RENTAL_MAINTENANCE_PERCENTAGE + settings.STRATEGY_RENTAL_CAPITAL_RESERVE_PERCENTAGE

        def metrics(rate_delta=0, rent_factor=1, expense_delta=0, vacancy_delta=0):
            gross = (rent or 0) * rent_factor * 12
            noi = gross * (1 - expense_rate - expense_delta - vacancy_delta)
            stressed_payment = 0 if kind == "cash" else ((loan * (rate + rate_delta) / 12) if io_months else cls.payment(loan, rate + rate_delta, amort_months))
            debt = stressed_payment * 12; annual_cash = noi - debt
            return {"debt_service_coverage_ratio": noi / debt if debt else None, "leveraged_annual_cash_flow": annual_cash, "leveraged_monthly_cash_flow": annual_cash / 12, "cash_on_cash_return": annual_cash / cash_required if cash_required else None}
        base = metrics(); expense_stress = expense_rate * .10
        stress_specs = [("base",0,1,0,0),("rate +1%",settings.FINANCING_MAX_RATE_STRESS,1,0,0),("rent -10%",0,.9,0,0),("expenses +10%",0,1,expense_stress,0),("vacancy +5 points",0,1,0,.05),("combined",settings.FINANCING_MAX_RATE_STRESS,.9,expense_stress,.05)]
        stress = [{"case": name, **metrics(dr, rf, de, dv)} for name,dr,rf,de,dv in stress_specs]
        balloon, total_interest = cls.amortization(loan, rate, amort_months, term, io_months, scenario.get("balloon_payment_month"))
        ltc = financed_basis / total_cost if total_cost else None; ltv = loan / value if value else None
        break_even = ((rent or 0) * 12 * expense_rate + annual_debt) / ((rent or 0) * 12) if rent else None
        reserve_months = (cls.number(scenario.get("reserve_requirement")) or 0) / active_debt if active_debt else None
        thresholds = {"minimum_dscr": settings.FINANCING_MIN_DSCR, "minimum_cash_on_cash_return": settings.FINANCING_MIN_CASH_ON_CASH_RETURN, "maximum_ltv": settings.FINANCING_MAX_LTV, "maximum_ltc": settings.FINANCING_MAX_LTC, "maximum_break_even_occupancy": settings.FINANCING_MAX_BREAK_EVEN_OCCUPANCY, "rate_stress": settings.FINANCING_MAX_RATE_STRESS, "minimum_reserve_months": settings.FINANCING_MIN_RESERVE_MONTHS}
        warnings = []
        if base["debt_service_coverage_ratio"] is not None and base["debt_service_coverage_ratio"] < settings.FINANCING_MIN_DSCR: warnings.append("DSCR is below the configured minimum.")
        if base["cash_on_cash_return"] is not None and base["cash_on_cash_return"] < settings.FINANCING_MIN_CASH_ON_CASH_RETURN: warnings.append("Cash-on-cash return is below the configured minimum.")
        if ltv is not None and ltv > settings.FINANCING_MAX_LTV: warnings.append("LTV exceeds the configured maximum.")
        if ltc is not None and ltc > settings.FINANCING_MAX_LTC: warnings.append("LTC exceeds the configured maximum.")
        if break_even is not None and break_even > settings.FINANCING_MAX_BREAK_EVEN_OCCUPANCY: warnings.append("Break-even occupancy is high.")
        if scenario.get("balloon_payment_month") or term < amort_months: warnings.append("Balloon risk: principal remains due before full amortization.")
        if io_months: warnings.append("Interest-only payment shock occurs when amortization begins.")
        if reserve_months is not None and reserve_months < settings.FINANCING_MIN_RESERVE_MONTHS: warnings.append("Reserves are below the configured minimum.")
        if base["leveraged_annual_cash_flow"] < 0: warnings.append("Leveraged cash flow is negative.")
        rate_case = stress[1]
        if base["debt_service_coverage_ratio"] is not None and rate_case["debt_service_coverage_ratio"] is not None and rate_case["debt_service_coverage_ratio"] < settings.FINANCING_MIN_DSCR <= base["debt_service_coverage_ratio"]: warnings.append("Debt coverage is sensitive to the configured rate increase.")
        combined = stress[-1]
        if combined["debt_service_coverage_ratio"] is not None and combined["debt_service_coverage_ratio"] < settings.FINANCING_MIN_DSCR: warnings.append("Combined stress materially weakens debt coverage.")
        if any("ARV" in item for item in missing): warnings.append("ARV is missing for rehab-oriented financing.")
        if missing: warnings.append("Analysis confidence is reduced by missing inputs.")
        confidence = max(0, min(1, ((resolved.get("rent_confidence") or 0) + (resolved.get("arv_confidence") if use_arv else resolved.get("current_value_confidence") or 0) + (resolved.get("rehab_confidence") or 0)) / 3 - .1 * len(missing)))
        return {"scenario_name": scenario["scenario_name"], "financing_type": kind, "monthly_principal_interest": monthly_pi, "monthly_interest_only": monthly_io, "annual_debt_service": annual_debt, "total_cash_required": cash_required, "financed_basis": financed_basis, "loan_to_cost": ltc, "loan_to_value": ltv, **base, "break_even_occupancy": break_even, "balloon_balance": balloon, "total_interest_over_term": total_interest, "analysis_confidence": confidence, "missing_inputs": missing, "warnings": warnings, "limitations": cls.LIMITATIONS, "formula_notes": ["Monthly amortizing payment = P × r(1+r)^n / ((1+r)^n − 1).", "DSCR = NOI / annual debt service; cash-on-cash = leveraged annual cash flow / total cash required.", "Tax-assessed value is excluded from value selection."], "stress_tests": stress, "threshold_snapshot": thresholds, "input_snapshot": {"purchase_price": purchase, "purchase_price_basis": purchase_basis, "loan_amount": loan, "down_payment_amount": down, "rehab_cost": rehab, "rehab_basis": resolved.get("rehab_basis"), "value": value, "value_basis": value_basis, "monthly_rent": rent, "rent_basis": resolved.get("rent_basis"), "annual_noi": (rent or 0) * 12 * (1-expense_rate), "tax_assessed_value_excluded": resolved.get("source_values", {}).get("tax_assessed_value_excluded"), "scenario": scenario}}
