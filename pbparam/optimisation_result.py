#
# Optimisation result class
#

import copy


class OptimisationResult(object):
    """
    Optimisation result class

    Parameters
    ----------
    x : array-like
        The solution of the optimisation.
    success : bool
        Whether or not the optimiser exited successfully.
    message : str
        Description of the cause of the termination.
    fun : float
        Value of the objective function.
    raw_result : scipy.optimize.OptimizeResult
        The raw result of the optimisation.
    """

    def __init__(self, x, success, message, fun, raw_result, optimisation_problem):
        self.x = x
        self.success = success
        self.message = message
        self.fun = fun
        self.raw_result = raw_result
        self.optimisation_problem = copy.deepcopy(optimisation_problem)

        # Initialise time
        self.solve_time = None

    def __str__(self):
        str = f'''
             Optimal values: {self.x}
        Cost function value: {self.fun}
                 Solve time: {self.solve_time}
                    Message: {self.message}
        '''

        return str

    def plot(self, testing=False):
        """
        Plot the optimisation result.
        """
        import matplotlib.pyplot as plt

        plot = self.optimisation_problem._plot(self.x)

        if not testing:  # pragma: no cover
            plt.show()

        return plot
