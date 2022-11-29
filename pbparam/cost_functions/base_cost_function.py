#
# Base cost function class
#

class BaseCostFunction():
    """
    Base cost function class
    """
    def __init__(self):
        self.data = None
        self.variables_optimise = None
        self.x = None
        self.scalings = None
        self.map_inputs = None
        self.simulation = None
        
    def cost_function(self, x):
        pass