#
# SciPy Minimize optimiser
#
import pbparam
import numpy as np
from scipy.optimize import minimize
import pybamm
import copy


class ScipyMinimize(pbparam.BaseOptimiser):
    """
    Scipy Minimize class.

    This class is a wrapper around the scipy.optimize.minimize function and
    uses various minimization methods.
    The 'Nelder-Mead' method is faster to converge and robust.Please refer to
    (https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html)
    for more details.

    Parameters
    ----------
    method : str or callable
        Type of solver. Should be one of

        ‘Nelder-Mead’

        ‘Powell’

        ‘CG’

        ‘BFGS’

        ‘Newton-CG’

        ‘L-BFGS-B’

        ‘TNC’

        ‘COBYLA’

        ‘SLSQP’

        ‘trust-constr’

        ‘dogleg’

        ‘trust-ncg’

        ‘trust-exact’

        ‘trust-krylov’

        custom - a callable object

    extra_options : dict, optional
        Dict of arguments that will be used in optimiser.
    """

    def __init__(self, method=None, extra_options=None, optimiser_options=None):
        super().__init__()
        self.method = method
        self.extra_options = extra_options or {}
        self.optimiser_options = optimiser_options or {}
        self.name = "SciPy Minimize optimiser with {} method".format(method)
        self.single_variable = False
        self.global_optimiser = False

    def _run_optimiser(self, optimisation_problem, x0, bounds):
        """
        Run the optimiser.

        Parameters
        ----------
        optimisation_problem : :class:`pbparam.OptimisationProblem`
            The optimization problem.
        x0 : array-like
            Initial guess of the solution.
        bounds : tuple
            Bounds of the variables.

        Returns
        -------
        result : :class:`pbparam.OptimisationResult`
            The result of the optimization.
        """
        self.optimisation_problem = copy.deepcopy(optimisation_problem)
        # Initialise timer
        timer = pybamm.Timer()

        raw_result = minimize(
            self.optimisation_problem.objective_function,
            x0,
            method=self.method,
            bounds=bounds,
            **self.extra_options,
            options=self.optimiser_options,
        )
        solve_time = timer.time()

        if optimisation_problem.scalings is None:
            scaled_result = raw_result.x
        else:
            scaled_result = np.multiply(raw_result.x, optimisation_problem.scalings)

        result_dict = {
            key: value
            for key, value in zip(
                self.optimisation_problem.parameters.keys(), scaled_result
            )
        }

        result = pbparam.OptimisationResult(
            result_dict,
            scaled_result,
            raw_result.success,
            raw_result.message,
            raw_result.fun,
            raw_result,
            self.optimisation_problem,
        )

        result.solve_time = solve_time

        return result
