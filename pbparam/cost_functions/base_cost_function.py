#
# Base cost function class
#

class BaseCostFunction():
    """
    Base cost function class
    """
    def __init__(self):
        # super().__init__()
        # self.name = "Cost function"
        self.y_sim = None
        self.y_data = None
        self.sd = None

    def cost_function(self):
        pass