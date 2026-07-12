class PropertyScorePlugin:

    def run(self, property_data):

        score = 50

        if property_data.property_type == "Vacant Land":
            score += 25

        if property_data.acres:

            if 0.2 <= property_data.acres <= 5:
                score += 15

        return score
    
    