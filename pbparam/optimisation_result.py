#
# Optimisation result class
#

from optparse import OptionError
import pybamm


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
        self.optimisation_problem = optimisation_problem

        # Initialise time
        self.solve_time = None

        # Initialise solutions
        self.initial_solution = None
        self.optimised_solution = None

    def calculate_solution(self, parameters="optimised"):
        """
        Calculate solution of model.

        Parameters
        ----------
        parameters : str (optional)
            Define if the simulation should be run with the optimised or initial
            parameters. It can be "optimised" (default) or "initial".

        Returns
        -------
        solution : pybamm.Solution
            The solution for the given inputs.
        """
        if parameters == "optimised":
            inputs = {
                param: self.x[i]
                for param, i in self.optimisation_problem.map_inputs.items()
            }
        elif parameters == "initial":
            inputs = {
                param: self.optimisation_problem.original_parameters[param]
                for param in self.optimisation_problem.map_inputs.keys()
            }
        else:
            raise OptionError(
                f"Parameters cannot be {parameters}, "
                "it must be either 'optimised' or 'initial'"
            )

        if getattr(self.optimisation_problem.simulation, "experiment", None):
            t_eval = None
        else:
            t_eval = [0, self.optimisation_problem.data["Time [s]"].iloc[-1]]

        solution = self.optimisation_problem.simulation.solve(
            t_eval=t_eval, inputs=inputs
        )

        return solution

    def plot(self, testing=False):
        """
        Plot the optimisation result.
        """
        import matplotlib.pyplot as plt
        
        if not self.initial_solution:
            self.initial_solution = self.calculate_solution(parameters="initial")
        if not self.optimised_solution:
            self.optimised_solution = self.calculate_solution(parameters="optimised")

        plot = pybamm.QuickPlot(
            [self.initial_solution, self.optimised_solution],
            output_variables=self.optimisation_problem.variables_optimise,
            labels=["Initial values", "Optimised values"],
        )

        plot.plot(0)

        for ax, var in zip(plot.axes, self.optimisation_problem.variables_optimise):
            data = self.optimisation_problem.data
            ax.plot(data["Time [s]"], data[var], "k:", label="Data")

        if not testing:  # pragma: no cover
            plt.show()

        return plot
