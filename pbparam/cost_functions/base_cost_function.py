#
# Base cost function class
#


class BaseCostFunction:
    """
    Base cost function class
    """

    def __init__(self):
        self.name = "Base Cost Function"

    def evaluate(self, y_sim, y_data, sd=None):
        pass
