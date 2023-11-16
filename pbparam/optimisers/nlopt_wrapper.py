import pbparam
import numpy as np
import nlopt
import pybamm
import copy


class Nlopt(pbparam.BaseOptimiser):
    """
    """

    def __init__(self, method, optimiser_target='minimise'):
        # Super the init from the base optimiser
        super().__init__()
        # Set the name of the optimiser
        self.name = "Nlopt"
        # would quite like to query the methods available from nlopt and compare
        self.method = method
        self.name = f"Nlopt optimiser with {self.method} method"
        # this could be the wrong place to do this bit but the optimiser needs to
        # be initialised with parameters and method
        if optimiser_target in ['minimise', 'min', 'minimize']:
            self.minimise = True
            self.maximise = False
        elif optimiser_target == ['maximise', 'max', 'maximize']:
            self.minimise = False
            self.maximise = True

    def _run_optimiser(self, optimisation_problem, x0, bounds):
        self.optimisation_problem = copy.deepcopy(optimisation_problem)
        
        # this wrapper appends the argument grad to the objective function
        # which is not used in this case
        def wrapper(function):
            def inner(*args):
                result = function(*args[:-1])
                return np.float64(result)
            return inner

        self.optimisation_problem.objective_function = \
            wrapper(self.optimisation_problem.objective_function)
        optimiser_dims = len(x0)
        opt = nlopt.opt(self.method, optimiser_dims)
        opt.set_xtol_rel(1e-4)
       
        u_bounds = []
        l_bounds = []
        for ix in range(len(bounds)):
            if bounds[ix][0] > bounds[ix][1]:
                u_bounds.append(bounds[ix][0])
                l_bounds.append(bounds[ix][1])
            else:
                u_bounds.append(bounds[ix][1])
                l_bounds.append(bounds[ix][0])

        opt.set_lower_bounds(l_bounds)
        opt.set_upper_bounds(u_bounds)

        if self.maximise:
            opt.set_max_objective(self.optimisation_problem.objective_function)
        elif self.minimise:
            opt.set_min_objective(self.optimisation_problem.objective_function)
        else:
            raise ValueError("Must specify whether to maximise or minimise")
        
        # Initialise timer
        timer = pybamm.Timer()
        raw_result = opt.optimize(x0)
        solve_time = timer.time()

        # Scale the result back to the original scale
        if optimisation_problem.scalings is None:
            scaled_result = raw_result
        else:
            scaled_result = np.multiply(raw_result, optimisation_problem.scalings)
        # Parse the result into a pbparam.OptimisationResult object
        result = pbparam.OptimisationResult(
            scaled_result,
            opt.last_optimize_result(),
            None,
            opt.last_optimum_value(),
            None,
            optimisation_problem,
        )
        result.solve_time = solve_time

        return result

