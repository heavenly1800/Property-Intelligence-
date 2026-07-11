from models import DealScore


class DealScorer:
    """
    Combines all available research into a single investment score.
    """

    def score(self, property_data: dict) -> DealScore:
        deal = DealScore()

        score = 50

        property_type = property_data.get("property_type")

        if property_type == "Vacant Land":
            score += 20
            deal.strengths.append(
                "Vacant land fits wholesale acquisition strategy."
            )

        years_owned = property_data.get("years_owned", 0)

        if years_owned >= 10:
            score += 10
            deal.strengths.append(
                "Long-term ownership suggests equity."
            )

        if property_data.get("utilities_available"):
            score += 10
            deal.strengths.append(
                "Utilities appear to be available."
            )

        if property_data.get("legal_access"):
            score += 10
            deal.strengths.append(
                "Legal road access identified."
            )

        if property_data.get("flood_zone"):
            score -= 15
            deal.risks.append(
                "Flood zone should be reviewed."
            )

        score = max(0, min(score, 100))

        deal.overall_score = score
        deal.confidence = score

        if score >= 85:
            deal.priority = "High"
        elif score >= 70:
            deal.priority = "Medium"
        else:
            deal.priority = "Low"

        return deal