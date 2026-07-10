from app.models.opportunity import Opportunity


class OpportunityService:

    @staticmethod
    def analyze(property_data):

        score = 50

        if property_data.property_type == "Vacant Land":
            score += 30

        strategy = (
            "Wholesale"
            if property_data.property_type == "Vacant Land"
            else "Buy & Hold"
        )

        confidence = 90

        next_action = "Research Owner"

        return Opportunity(
            property_id=property_data.property_id,
            score=score,
            strategy=strategy,
            confidence=confidence,
            next_action=next_action,
        )