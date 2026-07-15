from typing import Any


class FinancialAnalysisService:
    """Calculates financial outputs only from explicitly supplied inputs."""

    @classmethod
    def analyze(cls, data: dict[str, Any]) -> dict[str, Any]:
        unit_count = cls._number(data.get("unit_count"))
        current_monthly = cls._number(data.get("current_monthly_rent")) or (
            cls._number(data.get("current_monthly_rent_per_unit")) * unit_count
            if cls._number(data.get("current_monthly_rent_per_unit")) is not None and unit_count is not None
            else None
        )
        current_annual = cls._number(data.get("current_annual_rent")) or (
            current_monthly * 12 if current_monthly is not None else None
        )
        estimated_monthly = cls._number(data.get("estimated_monthly_rent")) or (
            cls._number(data.get("estimated_monthly_rent_per_unit")) * unit_count
            if cls._number(data.get("estimated_monthly_rent_per_unit")) is not None and unit_count is not None
            else None
        )
        estimated_annual = cls._number(data.get("estimated_annual_rent")) or (
            estimated_monthly * 12 if estimated_monthly is not None else None
        )
        gross_rent = current_annual if current_annual is not None else estimated_annual
        expense_percent = cls._number(data.get("expected_operating_expense_percentage"))
        expenses_annual = (
            gross_rent * expense_percent / 100
            if gross_rent is not None and expense_percent is not None
            else None
        )
        noi = gross_rent - expenses_annual if expenses_annual is not None else None
        asking_price = cls._number(data.get("asking_price"))
        arv_low = cls._number(data.get("estimated_after_repair_value_low")) or cls._number(data.get("after_repair_value"))
        arv_high = cls._number(data.get("estimated_after_repair_value_high")) or cls._number(data.get("after_repair_value"))
        rehab_low = cls._number(data.get("estimated_rehab_cost_low"))
        rehab_high = cls._number(data.get("estimated_rehab_cost_high"))
        post_rehab_monthly = cls._number(data.get("estimated_post_rehab_monthly_rent"))
        financial_missing_items = cls._missing_items(
            data, gross_rent, expense_percent, arv_low, arv_high, rehab_low, rehab_high
        )

        return {
            "current_annual_rent": current_annual,
            "estimated_annual_rent": estimated_annual,
            "estimated_operating_expenses_annual": expenses_annual,
            "estimated_operating_expenses_monthly": expenses_annual / 12 if expenses_annual is not None else None,
            "estimated_noi_annual": noi,
            "estimated_cap_rate": noi / asking_price if noi is not None and asking_price else None,
            "gross_rent_multiplier": asking_price / gross_rent if asking_price and gross_rent else None,
            "estimated_monthly_cash_flow": None,
            "estimated_after_repair_value_low": arv_low,
            "estimated_after_repair_value_high": arv_high,
            "estimated_flip_profit_low": arv_low - asking_price - rehab_high if arv_low is not None and asking_price is not None and rehab_high is not None else None,
            "estimated_flip_profit_high": arv_high - asking_price - rehab_low if arv_high is not None and asking_price is not None and rehab_low is not None else None,
            "estimated_post_rehab_annual_rent": post_rehab_monthly * 12 if post_rehab_monthly is not None else None,
            "financial_analysis_confidence": cls._confidence(asking_price, gross_rent, expense_percent),
            "financial_missing_items": financial_missing_items,
            "recommended_financial_action": cls._action(financial_missing_items),
        }

    @staticmethod
    def _number(value: Any) -> float | None:
        return float(value) if isinstance(value, (int, float)) else None

    @staticmethod
    def _missing_items(data: dict[str, Any], gross_rent: float | None, expense_percent: float | None, arv_low: float | None, arv_high: float | None, rehab_low: float | None, rehab_high: float | None) -> list[str]:
        checks = (
            (not data.get("asking_price"), "Asking price"),
            (not data.get("unit_count"), "Unit count"),
            (gross_rent is None, "Current or estimated rent"),
            (expense_percent is None, "Operating-expense percentage"),
            (not data.get("occupancy_status"), "Occupancy status"),
            (not data.get("property_condition"), "Property condition"),
            (arv_low is None or arv_high is None, "ARV estimate"),
            (rehab_low is None or rehab_high is None, "Rehab cost range"),
        )
        return [item for missing, item in checks if missing]

    @staticmethod
    def _confidence(asking_price: float | None, gross_rent: float | None, expense_percent: float | None) -> str:
        if asking_price is not None and gross_rent is not None and expense_percent is not None:
            return "high"
        if asking_price is not None and gross_rent is not None:
            return "medium"
        return "low"

    @staticmethod
    def _action(missing_items: list[str]) -> str:
        if not missing_items:
            return "Verify financing, holding, and disposition assumptions before underwriting."
        return f"Enter {missing_items[0].lower()} to complete financial analysis."
