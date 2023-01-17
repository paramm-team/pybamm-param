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
    Scipy Minimize class. Please refer to
    (https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html)
    for more details. Scipy Minimize has various minimasiation methods.
    'Nelder-Mead' method is faster to converge and robust.

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
            self.optimisation_problem.objective_function,
            x0,
            method=self.method,
            bounds=bounds,
            **self.extra_options,
            options=self.solver_options,
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
            self.optimisation_problem,
        )

        result.solve_time = solve_time

        return result
