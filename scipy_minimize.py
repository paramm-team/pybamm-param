#
# SciPy Minimize optimiser
#

from scipy.optimize import minimize
from base_optimiser import BaseOptimiser
from optimisation_result import OptimisationResult
import pybamm
import copy


class ScipyMinimize(BaseOptimiser):
    """
    TODO: write
    """

    def __init__(self, method=None, extra_options=None):
        super().__init__()
        self.method = method
        self.extra_options = extra_options or {}
        self.name = "SciPy Minimize optimiser with {} method".format(method)
        self.single_variable = False
        self.global_optimiser = False

    def _run_optimiser(self, optimisation_problem, x0, bounds):
        self.optimisation_problem = copy.deepcopy(optimisation_problem)
        # Initialise timer
        timer = pybamm.Timer()

        raw_result = minimize(
            self.optimisation_problem.cost_function,
            x0,
            method=self.method,
            bounds=bounds,
            **self.extra_options
        )
        solve_time = timer.time()

        result = OptimisationResult(
            raw_result.x,
            raw_result.success,
            raw_result.message,
            raw_result.fun,
            raw_result,
            self.optimisation_problem,
        )

        result.solve_time = solve_time

        return result
