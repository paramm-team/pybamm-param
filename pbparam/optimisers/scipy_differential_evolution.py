#
# SciPy Differential Evolution optimiser
#
import pbparam
import numpy as np
from scipy.optimize import differential_evolution
import pybamm


class ScipyDifferentialEvolution(pbparam.BaseOptimiser):
    """
    Scipy Differential Evolution Optimiser class. Wraps the Scipy's differential 
    evolution optimizer for use in an optimization problem.
    Inherits from the BaseOptimizer class and overrides the _run_optimizer method 
    to use the differential_evolution function from Scipy's optimize module.
    Please refer to
    (https://docs.scipy.org/doc/scipy/reference/generated/
    scipy.optimize.differential_evolution.html) for more details.
    Scipy Differential Evolution is a non-gradient based method that is robust but
    slower to converge than 'Nelder-Mead' method.

    Parameters
    ----------
    extra_options : dict, optional
        Dict of arguments that will be passed to the differential_evolution function.

    Attributes
    ----------
    name : str
        The name of the optimizer.
    single_variable : bool
        Indicates if the optimizer only accepts a single variable.
    global_optimizer : bool
        Indicates if the optimizer is a global optimizer.

    """

    def __init__(self, extra_options=None):
        super().__init__()
        self.extra_options = extra_options or {}
        self.name = "SciPy Differential Evolution optimiser"
        self.single_variable = False
        self.global_optimiser = True

    def _run_optimiser(self, optimisation_problem, x0, bounds):
        """
        Runs the optimization process.
        
        Parameters
        ----------
        optimisation_problem : :class:`pbparam.OptimisationProblem`
            The optimization problem to solve.
        x0 : array_like
            Initial guess for the optimization problem.
        bounds : array_like
            Bounds for the optimization problem.

        Returns
        -------
        result : :class:`pbparam.pbparam.OptimisationResult`
            The results of the optimization process.

        """
        timer = pybamm.Timer()
        raw_result = differential_evolution(
            optimisation_problem.objective_function,
            bounds,
            x0=x0,
            **self.extra_options,
        )
        solve_time = timer.time()
        if optimisation_problem.scalings is None:
            scaled_result = raw_result.x
        else:
            scaled_result = np.multiply(raw_result.x, optimisation_problem.scalings)

        result = pbparam.OptimisationResult(
            scaled_result,
            raw_result.success,
            raw_result.message,
            raw_result.fun,
            raw_result,
            optimisation_problem,
        )
        result.solve_time = solve_time
        return result
