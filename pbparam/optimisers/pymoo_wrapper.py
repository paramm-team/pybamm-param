#
# SciPy Minimize optimiser
#
import pbparam
import numpy as np
from pymoo.optimize import minimize
from pymoo.core.problem import Problem
from pymoo.algorithms.moo.nsga2 import NSGA2
import pybamm
import copy


class new_objective_function(Problem):
    def __init__(self, optimisation_problem, x0, bounds):
        self.x0 = x0
        lb = [bounds[i][0] for i in range(len(bounds))]
        ub = [bounds[i][1] for i in range(len(bounds))]
        super().__init__(
            n_var=len(x0),
            n_obj=1,
            n_constr=0,
            xl=lb,
            xu=ub)
        self.optimisation_problem = optimisation_problem

    def _evaluate(self, x, out, *args, **kwargs):
        out["F"] = [self.optimisation_problem.objective_function(i) for i in x]


class PymooMinimize(pbparam.BaseOptimiser):
    """
    Pymoo Minimize class.

    This class is a wrapper around the pymoo minimize function and
    uses various minimization methods.
    We can use:
    https://pymoo.org/algorithms/list.html#nb-algorithms-list


    Parameters
    ----------
    method : str or callable
        Type of solver. https://pymoo.org/algorithms/list.html#nb-algorithms-list
    """

    def __init__(self, method=NSGA2):
        super().__init__()
        self.method = NSGA2()
        self.name = f"PyMoo Minimize optimiser with {method} method"
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
        self.objective_function = new_objective_function(
            self.optimisation_problem,
            x0,
            bounds
        )
        # Initialise timer
        timer = pybamm.Timer()

        raw_result = minimize(
            self.objective_function,
            self.method,
        )
        solve_time = timer.time()

        if optimisation_problem.scalings is None:
            scaled_result = raw_result.X
        else:
            scaled_result = np.multiply(raw_result.X, optimisation_problem.scalings)

        result = pbparam.OptimisationResult(
            scaled_result,
            raw_result.success,
            raw_result.message,
            raw_result.f,
            raw_result,
            self.optimisation_problem,
        )

        result.solve_time = solve_time

        return result
