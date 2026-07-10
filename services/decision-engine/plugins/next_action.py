class NextActionPlugin:

    def run(self, property_data):

        if property_data.property_type == "Vacant Land":
            return "Research Owner"

        return "Analyze Further"