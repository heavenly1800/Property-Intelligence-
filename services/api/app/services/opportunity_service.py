from app.models.opportunity import Opportunity


class OpportunityService:

    @staticmethod
    def analyze(property_data: dict):
        """Describe evaluation state without inventing a score or confidence."""
        researched = property_data.get("research_quality_score") is not None
        next_action = (
            "Run Deal Strategy analysis."
            if researched
            else "Complete property research before evaluating the opportunity."
        )

        return Opportunity(
            property_id=property_data.get("property_id"),
            score=None,
            strategy=None,
            confidence=None,
            next_action=next_action,
            evaluation_status="not_evaluated",
        )
