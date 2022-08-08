#
# Shared methods and classes for testing
#


class DummyOptimisationProblem:
    """
    Dummy optimisation problem for testing
    """

    def __init__(self):
        self.x0 = None
        self.bounds = None

    def cost_function(self, x):
        pass

    def setup_cost_function(self):
        pass
