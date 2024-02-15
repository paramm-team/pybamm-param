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
    optimisation_problem : object
        The optimisation problem that was used for the optimization.
    """

    def __init__(self, x, success, message, fun, raw_result, optimisation_problem, optimiser_name):
        """
        Initialize the OptimisationResult class
        """
        self.x = x
        self.success = success
        self.message = message
        self.fun = fun
        self.raw_result = raw_result
        self.optimisation_problem = copy.deepcopy(optimisation_problem)
        self.optimiser_name = optimiser_name

        # Initialise time
        self.solve_time = None
        self.result_dict = {
            key: x[value] for key, value in self.optimisation_problem.map_inputs.items()
        }
        self.initial_guess = {
            key: self.optimisation_problem.x0[value]
            for key, value in self.optimisation_problem.map_inputs.items()
        }
        self.bounds = {
            key: self.optimisation_problem.bounds[value]
            for key, value in self.optimisation_problem.map_inputs.items()
        }

    def __str__(self):
        str = f"""
             Optimal values: {self.result_dict}
             Initial values: {self.initial_guess}
                  Optimiser: {self.optimiser_name}
        Cost function value: {self.fun}
                 Solve time: {self.solve_time}
                    Message: {self.message}
        """

        return str

    def plot(self, testing=False):
        """
        Plot the optimisation result.

        Parameters
        ----------
        testing : bool, optional
            If True, the plot is not shown. The default is False.

        Returns
        -------
        plot : object
            The plot object.
        """
        import matplotlib.pyplot as plt

        plot = self.optimisation_problem._plot(self.x)

        if not testing:  # pragma: no cover
            plt.show()

        return plot
