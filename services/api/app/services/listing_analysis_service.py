import re
from datetime import datetime, timezone


class ListingAnalysisService:
    @classmethod
    def analyze(cls, text: str) -> dict:
        fields = {}
        patterns = {"asking_price": (r"\$([\d,]+)", cls.money), "unit_count": (r"\b(\d+)\s*[- ]?unit\b", int), "bedrooms": (r"\b(\d+)\s*(?:bed|br)\b", int), "bathrooms": (r"\b(\d+(?:\.\d+)?)\s*(?:bath|ba)\b", float), "square_feet": (r"\b([\d,]+)\s*(?:sq\.?\s*ft|square feet)\b", cls.number), "year_built": (r"(?:built|year built)\D*(\d{4})", int)}
        for key, (pattern, cast) in patterns.items():
            match = re.search(pattern, text, re.I)
            if match: fields[key] = cast(match.group(1))
        highlights = [item for item in ("Stated upgrades" if re.search(r"updated|renovat|remodel", text, re.I) else None, "Utility information disclosed" if re.search(r"water|sewer|electric|gas", text, re.I) else None) if item]
        risks = [item for item in ("Condition concerns disclosed" if re.search(r"as[- ]is|repair|deferred|fixer|damage", text, re.I) else None, "Vacancy disclosed" if re.search(r"vacant", text, re.I) else None) if item]
        missing = [label for key, label in (("asking_price", "Asking price"), ("unit_count", "Unit count"), ("bedrooms", "Bedrooms"), ("bathrooms", "Bathrooms"), ("square_feet", "Square feet"), ("year_built", "Year built")) if key not in fields]
        return {**fields, "listing_raw_text": text, "listing_summary": "Listing text parsed from manually supplied content.", "listing_highlights": highlights, "listing_risks": risks, "listing_missing_items": missing, "listing_last_analyzed_at": datetime.now(timezone.utc).isoformat(), "listing_analysis_status": "completed"}
    @staticmethod
    def money(value: str): return float(value.replace(",", ""))
    @staticmethod
    def number(value: str): return int(value.replace(",", ""))
