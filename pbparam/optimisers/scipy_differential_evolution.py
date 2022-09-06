#
# SciPy Differential Evolution optimiser
#
import pbparam
import numpy as np
from scipy.optimize import differential_evolution
import pybamm


class ScipyDifferentialEvolution(pbparam.BaseOptimiser):
    """
    TODO: write
    """

    def __init__(self, extra_options=None):
        super().__init__()
        self.extra_options = extra_options or {}
        self.name = "SciPy Differential Evolution optimiser"
        self.single_variable = False
        self.global_optimiser = True

    def _run_optimiser(self, optimisation_problem, x0, bounds):
        # Initialise timer
        timer = pybamm.Timer()

        raw_result = differential_evolution(
            optimisation_problem.cost_function,
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
