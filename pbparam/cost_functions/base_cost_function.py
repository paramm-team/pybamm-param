#
# Base optimisation problem class
#

class BaseCostFunction():
    """
    Base optimisation problem class
    """
    def __init__(self):
        self.data = None
        self.variables_optimise = None
        self.x = None
        self.scalings = None
        self.map_inputs = None
        self.simulation = None