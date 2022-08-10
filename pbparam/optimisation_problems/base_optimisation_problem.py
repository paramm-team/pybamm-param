#
# Base optimisation problem class
#

class BaseOptimisationProblem():
    """
    Base optimisation problem class
    """
    def __init__(self):
        self.x0 = None
        self.bounds = None

    def cost_function(self, x):
        pass

    def setup_cost_function(self):
        pass

    def calculate_solution(self):
        pass

    def _plot(self):
        pass
