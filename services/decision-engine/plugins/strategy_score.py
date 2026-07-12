class StrategyScorePlugin:

    def run(self, property_data):

        if property_data.property_type == "Vacant Land":
            return "Wholesale"

        return "Hold"
    