from datetime import date, datetime, timezone
from statistics import median

from app.core.settings import get_settings


class ComparableAnalysisService:
    RENOVATED_CONDITIONS = {"renovated", "updated", "excellent", "superior"}
    MULTIFAMILY_TYPES = {"multifamily", "multi-family", "duplex", "triplex", "fourplex", "apartment"}

    @staticmethod
    def _ratio_score(subject, comparable, points: float) -> float:
        if subject in (None, 0) or comparable in (None, 0): return points * .5
        return points * max(0, 1 - abs(float(subject) - float(comparable)) / max(float(subject), float(comparable)))

    @staticmethod
    def _age_days(item: dict, today: date) -> int | None:
        raw = item.get("sale_date") if item.get("comparable_type") == "sale" else item.get("listing_date")
        if not raw: return None
        value = date.fromisoformat(str(raw)[:10])
        return max(0, (today - value).days)

    @classmethod
    def exclusion_reason(cls, subject: dict, item: dict, seen: set[tuple], today: date) -> str | None:
        settings = get_settings()
        if not item.get("included", True) and item.get("exclusion_reason") == "manually excluded": return "manually excluded"
        if not str(item.get("source_name") or "").strip() or not str(item.get("source_url") or "").startswith(("http://", "https://")): return "unverifiable source"
        identity = (str(item.get("source_name")).lower(), item.get("source_record_id") or item.get("source_url"))
        if identity in seen: return "duplicate source record"
        seen.add(identity)
        if item.get("distance_miles") is None or float(item["distance_miles"]) > settings.COMPARABLE_MAX_DISTANCE_MILES: return "excessive distance"
        age = cls._age_days(item, today)
        max_age = settings.COMPARABLE_MAX_SALE_AGE_DAYS if item.get("comparable_type") == "sale" else settings.COMPARABLE_MAX_RENTAL_AGE_DAYS
        if age is None or age > max_age: return "stale sale/listing date"
        if item.get("comparable_type") == "sale" and not item.get("sale_price"): return "missing sale price"
        if item.get("comparable_type") == "rental" and not item.get("monthly_rent"): return "missing monthly rent"
        subject_type, comp_type = str(subject.get("property_type") or "").lower(), str(item.get("property_type") or "").lower()
        subject_multi = subject_type in cls.MULTIFAMILY_TYPES or int(subject.get("unit_count") or 1) > 1
        comp_multi = comp_type in cls.MULTIFAMILY_TYPES or int(item.get("unit_count") or 1) > 1
        if subject_type and comp_type and subject_multi != comp_multi: return "incompatible property type; multifamily and single-family evidence cannot be directly compared"
        subject_units, comp_units = int(subject.get("unit_count") or 1), int(item.get("unit_count") or 1)
        if max(subject_units, comp_units) / min(subject_units, comp_units) > 2: return "materially different unit count"
        return None

    @classmethod
    def score(cls, subject: dict, item: dict, today: date | None = None) -> tuple[float, dict]:
        today = today or date.today(); settings = get_settings()
        distance = float(item.get("distance_miles") or settings.COMPARABLE_MAX_DISTANCE_MILES)
        age = cls._age_days(item, today) or 0
        max_age = settings.COMPARABLE_MAX_SALE_AGE_DAYS if item["comparable_type"] == "sale" else settings.COMPARABLE_MAX_RENTAL_AGE_DAYS
        components = {
            "distance": 20 * max(0, 1 - distance / settings.COMPARABLE_MAX_DISTANCE_MILES),
            "recency": 20 * max(0, 1 - age / max_age),
            "property_type": 12 if str(subject.get("property_type") or "").lower() == str(item.get("property_type") or "").lower() else 5,
            "property_subtype": 8 if subject.get("property_subtype") and str(subject.get("property_subtype")).lower() == str(item.get("property_subtype") or "").lower() else 3,
            "unit_count": cls._ratio_score(subject.get("unit_count"), item.get("unit_count"), 15),
            "bedrooms": cls._ratio_score(subject.get("bedrooms"), item.get("bedrooms"), 5),
            "bathrooms": cls._ratio_score(subject.get("bathrooms"), item.get("bathrooms"), 4),
            "square_feet": cls._ratio_score(subject.get("square_feet"), item.get("square_feet"), 8),
            "lot_size": cls._ratio_score(subject.get("acres") or subject.get("parcel_acres"), item.get("lot_acres"), 3),
            "year_built": cls._ratio_score(subject.get("year_built"), item.get("year_built"), 2),
            "condition_relevance": 1 if subject.get("property_condition") and str(subject.get("property_condition")).lower() == str(item.get("condition") or "").lower() else .5,
            "rehab_similarity": 1 if bool(subject.get("rehab_needed")) == (str(item.get("condition") or "").lower() not in cls.RENOVATED_CONDITIONS) else .5,
            "sale_rental_relevance": 1,
        }
        return round(sum(components.values()), 2), components

    @classmethod
    def weight(cls, subject: dict, item: dict, today: date) -> float:
        settings = get_settings(); score = float(item["match_score"]) / 100
        age = cls._age_days(item, today) or 0
        max_age = settings.COMPARABLE_MAX_SALE_AGE_DAYS if item["comparable_type"] == "sale" else settings.COMPARABLE_MAX_RENTAL_AGE_DAYS
        recency = max(.1, 1 - age / max_age); distance = 1 / (1 + float(item.get("distance_miles") or settings.COMPARABLE_MAX_DISTANCE_MILES))
        unit = cls._ratio_score(subject.get("unit_count"), item.get("unit_count"), 1)
        sqft = cls._ratio_score(subject.get("square_feet"), item.get("square_feet"), 1)
        condition = 1 if str(subject.get("property_condition") or "").lower() == str(item.get("condition") or "").lower() else .8
        return max(.001, score * recency * distance * unit * sqft * condition)

    @staticmethod
    def _weighted_estimate(items: list[dict], value_key: str) -> tuple[float, float, float]:
        ordered = sorted(items, key=lambda x: float(x[value_key])); total_weight = sum(x["_weight"] for x in ordered)
        central = sum(float(x[value_key]) * x["_weight"] for x in ordered) / total_weight
        def percentile(target):
            running = 0.0
            for item in ordered:
                running += item["_weight"]
                if running / total_weight >= target: return float(item[value_key])
            return float(ordered[-1][value_key])
        return round(percentile(.2), 2), round(central, 2), round(percentile(.8), 2)

    @classmethod
    def analyze(cls, subject: dict, comparables: list[dict], today: date | None = None) -> tuple[list[dict], dict]:
        today = today or date.today(); settings = get_settings(); seen: set[tuple] = set(); prepared = []
        for source in comparables:
            item = dict(source)
            reason = cls.exclusion_reason(subject, item, seen, today)
            score, components = cls.score(subject, item, today)
            sqft = float(item.get("square_feet") or 0); units = float(item.get("unit_count") or 0)
            item.update({"match_score": score, "score_components": components, "price_per_square_foot": float(item["sale_price"]) / sqft if item.get("sale_price") and sqft else None, "price_per_unit": float(item["sale_price"]) / units if item.get("sale_price") and units else None, "rent_per_unit": float(item["monthly_rent"]) / units if item.get("monthly_rent") and units else None, "rent_per_square_foot": float(item["monthly_rent"]) / sqft if item.get("monthly_rent") and sqft else None, "included": reason is None, "exclusion_reason": reason})
            prepared.append(item)

        for comparable_type, value_key in (("sale", "sale_price"), ("rental", "monthly_rent")):
            candidates = [x for x in prepared if x["included"] and x["comparable_type"] == comparable_type]
            if len(candidates) >= 3:
                center = median(float(x[value_key]) for x in candidates)
                for item in candidates:
                    if abs(float(item[value_key]) - center) / center > settings.COMPARABLE_OUTLIER_DEVIATION:
                        item["included"] = False; item["exclusion_reason"] = f"outlier {value_key.replace('_', ' ')}"

        included_sales = [x for x in prepared if x["included"] and x["comparable_type"] == "sale"]
        included_rentals = [x for x in prepared if x["included"] and x["comparable_type"] == "rental"]
        for item in included_sales + included_rentals: item["_weight"] = cls.weight(subject, item, today)
        current = cls._weighted_estimate(included_sales, "sale_price") if len(included_sales) >= settings.COMPARABLE_MIN_SALES else None
        rentals = cls._weighted_estimate(included_rentals, "monthly_rent") if len(included_rentals) >= settings.COMPARABLE_MIN_RENTALS else None
        renovated = [x for x in included_sales if str(x.get("condition") or "").lower() in cls.RENOVATED_CONDITIONS]
        arv = cls._weighted_estimate(renovated, "sale_price") if len(renovated) >= settings.COMPARABLE_MIN_SALES else None
        for item in prepared: item.pop("_weight", None)
        missing = []
        if current is None: missing.append(f"At least {settings.COMPARABLE_MIN_SALES} included sale comparables")
        if rentals is None: missing.append(f"At least {settings.COMPARABLE_MIN_RENTALS} included rental comparables")
        if arv is None: missing.append(f"At least {settings.COMPARABLE_MIN_SALES} included renovated/superior sale comparables for ARV")
        included = included_sales + included_rentals
        avg_score = sum(float(x["match_score"]) for x in included) / len(included) if included else 0
        confidence = round(min(1, avg_score / 100) * min(1, len(included_sales) / settings.COMPARABLE_MIN_SALES) * min(1, len(included_rentals) / settings.COMPARABLE_MIN_RENTALS), 2)
        analysis = {
            "property_id": subject["property_id"], "current_market_value_low": current[0] if current else None, "estimated_market_value": current[1] if current else None, "current_market_value_high": current[2] if current else None,
            "after_repair_value_low": arv[0] if arv else None, "estimated_after_repair_value": arv[1] if arv else None, "after_repair_value_high": arv[2] if arv else None,
            "estimated_monthly_market_rent_low": rentals[0] if rentals else None, "estimated_monthly_market_rent": rentals[1] if rentals else None, "estimated_monthly_market_rent_high": rentals[2] if rentals else None,
            "estimated_annual_market_rent": rentals[1] * 12 if rentals else None, "sale_comparable_count": len(included_sales), "rental_comparable_count": len(included_rentals),
            "average_sale_distance": round(sum(float(x["distance_miles"]) for x in included_sales) / len(included_sales), 2) if included_sales else None,
            "average_rental_distance": round(sum(float(x["distance_miles"]) for x in included_rentals) / len(included_rentals), 2) if included_rentals else None,
            "comparable_analysis_confidence": confidence, "comparable_analysis_status": "complete" if not missing else "insufficient_evidence",
            "comparable_missing_items": missing, "comparable_limitations": ["Manual source evidence has not been independently verified.", "Estimates exclude tax-assessed values, asking price, manual ARV/rent, and AI rehab costs.", "Comparable quality depends on accurate condition, unit-count, distance, and date inputs."],
            "recommended_comparable_action": "Review source records and confirm condition adjustments." if not missing else f"Add {missing[0].lower()}.", "analyzed_at": datetime.now(timezone.utc).isoformat(),
        }
        return prepared, analysis


ComparableService = ComparableAnalysisService
