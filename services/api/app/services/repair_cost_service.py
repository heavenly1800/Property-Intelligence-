from app.infrastructure.database.repair_cost_repository import RepairCostRepository


class RepairCostService:
    VERSION = "regional-visible-repair-2026.1"
    DISCLAIMER = "Editable underwriting assumptions only; not contractor bids or a live contractor database."
    LIMITATIONS = [
        "Image-derived quantities are approximate and may omit concealed or unphotographed work.",
        "Pricing excludes permits, design, hazardous-material remediation, and hidden-condition change orders unless explicitly listed.",
        DISCLAIMER,
    ]

    CATEGORY_ALIASES = {
        "paint": "interior paint", "doors": "interior doors", "electrical": "electrical visible repairs",
        "plumbing": "plumbing fixture repairs", "hvac": "HVAC visible service/replacement allowance",
    }

    @classmethod
    def normalize_category(cls, category: str, area: str = "") -> str:
        value = category.strip().lower()
        if value == "paint":
            return "exterior paint" if "exterior" in area.lower() else "interior paint"
        return cls.CATEGORY_ALIASES.get(value, value)

    @staticmethod
    def _same(left, right) -> bool:
        def normalized(value):
            text = str(value).strip().lower()
            return text[:-7].strip() if text.endswith(" county") else text
        return bool(left and right and normalized(left) == normalized(right))

    @classmethod
    def select_profile(cls, property_data: dict, profiles: list[dict]) -> tuple[dict, float, str]:
        active = list(profiles)
        exact = [p for p in active if cls._same(p.get("city"), property_data.get("city")) and cls._same(p.get("zip_code"), property_data.get("zip_code"))]
        if exact: return exact[0], 1.0, "exact city/zip match"
        county = [p for p in active if cls._same(p.get("county"), property_data.get("county")) and cls._same(p.get("state"), property_data.get("state"))]
        if county: return county[0], 0.85, "county match"
        state = [p for p in active if p.get("state") and cls._same(p.get("state"), property_data.get("state")) and not p.get("county")]
        if state: return state[0], 0.65, "state match"
        default = next((p for p in active if p.get("is_default")), None)
        if not default: raise ValueError("A default repair cost profile is required.")
        return default, 0.4, "default national fallback"

    @classmethod
    def price_analysis(cls, items: list[dict], property_data: dict, profiles=None, cost_items=None) -> dict:
        profiles = RepairCostRepository.list_profiles() if profiles is None else profiles
        profile, match_confidence, match_reason = cls.select_profile(property_data, profiles)
        costs = RepairCostRepository.list_items(profile["profile_id"]) if cost_items is None else cost_items
        by_category = {str(item["category"]).lower(): item for item in costs}
        priced, subtotal_low, subtotal_high = [], 0.0, 0.0
        contingency_rate = 0.0

        for source in items:
            category = cls.normalize_category(source["category"], source.get("area", ""))
            assumption = by_category.get(category.lower()) or by_category.get("general contingency")
            if not assumption: raise ValueError(f"No repair-cost assumption for {category}.")
            if category == "general contingency" or assumption["unit_type"] == "percentage contingency":
                contingency_rate = max(contingency_rate, float(assumption.get("contingency_percentage") or 0) / 100)
                continue

            quantity_low = source.get("estimated_quantity_low")
            quantity_high = source.get("estimated_quantity_high")
            legacy_quantity = source.get("scope_units")
            if quantity_low is None and legacy_quantity is not None: quantity_low = float(legacy_quantity)
            if quantity_high is None and legacy_quantity is not None: quantity_high = float(legacy_quantity)
            defensible_quantity = quantity_low is not None and quantity_high is not None
            q_low = max(0.0, float(quantity_low or 0))
            q_high = max(q_low, float(quantity_high or 0))
            unit_low = float(assumption["cost_low_per_unit"])
            unit_high = float(assumption["cost_high_per_unit"])
            minimum_low = float(assumption["minimum_job_cost_low"])
            minimum_high = float(assumption["minimum_job_cost_high"])
            extended_low = max(minimum_low, q_low * unit_low) if defensible_quantity else minimum_low
            extended_high = max(minimum_high, q_high * unit_high) if defensible_quantity else minimum_high
            priced.append({
                **source, "category": category, "estimated_quantity_low": quantity_low,
                "estimated_quantity_high": quantity_high, "quantity_unit": source.get("quantity_unit") or assumption["unit_type"],
                "quantity_confidence": float(source.get("quantity_confidence") or 0),
                "unit_cost_low": unit_low, "unit_cost_high": unit_high,
                "extended_cost_low": extended_low, "extended_cost_high": extended_high,
                "estimated_cost_low": extended_low, "estimated_cost_high": extended_high,
                "assumption_notes": assumption.get("labor_material_notes"),
                "cost_confidence": min(float(profile.get("confidence") or 0), float(source.get("quantity_confidence") or 0)) if defensible_quantity else min(float(profile.get("confidence") or 0), 0.35),
                "regional_profile_id": profile["profile_id"], "regional_profile_name": profile["profile_name"],
                "minimum_job_cost_applied": not defensible_quantity or extended_low == minimum_low or extended_high == minimum_high,
            })
            subtotal_low += extended_low
            subtotal_high += extended_high

        contingency_assumption = by_category.get("general contingency")
        contingency_rate = contingency_rate or float((contingency_assumption or {}).get("contingency_percentage") or 0) / 100
        contingency_low = subtotal_low * contingency_rate
        contingency_high = subtotal_high * contingency_rate
        return {
            "items": priced, "visible_repair_subtotal_low": subtotal_low, "visible_repair_subtotal_high": subtotal_high,
            "contingency_low": contingency_low, "contingency_high": contingency_high,
            "total_low": subtotal_low + contingency_low, "total_high": subtotal_high + contingency_high,
            "profile": profile, "profile_match_confidence": match_confidence, "profile_match_reason": match_reason,
            "cost_assumption_effective_date": profile["effective_date"], "cost_limitations": cls.LIMITATIONS,
        }
