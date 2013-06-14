class Attribute:
    """
    Each attribute has a name and a set of value values
    The name is the name of the attribute (ex. "weather"),
    Values are the different states an attribute can have (ex. "sunny", "cloudy", "rainy")
    """
    def __init__(self, name, values):
        self.name = name
        self.values = values
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return "Attribute('" + str(self.name) + "', " + str(self.values) + ")"
