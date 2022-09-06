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
    TODO: write
    """

    def __init__(self, method=None, extra_options=None, solver_options=None):
        super().__init__()
        self.method = method
        self.extra_options = extra_options or {}
        self.solver_options = solver_options or {}
        self.name = "SciPy Minimize optimiser with {} method".format(method)
        self.single_variable = False
        self.global_optimiser = False

    def _run_optimiser(self, optimisation_problem, x0, bounds):
        """
        Run the optimiser.
        """
        self.optimisation_problem = copy.deepcopy(optimisation_problem)
        # Initialise timer
        timer = pybamm.Timer()

        raw_result = minimize(
            self.optimisation_problem.cost_function,
            x0,
            method=self.method,
            bounds=bounds,
            **self.extra_options,
            options=self.solver_options,
        )
        solve_time = timer.time()

        if optimisation_problem.scalings:
            scaled_result = np.multiply(raw_result.x, optimisation_problem.scalings)
        else:
            scaled_result = raw_result.x

        result = pbparam.OptimisationResult(
            scaled_result,
            raw_result.success,
            raw_result.message,
            raw_result.fun,
            raw_result,
            self.optimisation_problem,
        )

        result.solve_time = solve_time

        return result
