import pbparam
import numpy as np
import nlopt
import pybamm
import copy


class Nlopt(pbparam.BaseOptimiser):
    """
    """

    def __init__(self, method, optimiser_dims, optimiser_target='minimise'):
        # Super the init from the base optimiser
        super().__init__()
        # Set the name of the optimiser
        self.name = "Nlopt"
        # would quite like to query the methods available from nlopt and compare
        self.method = method
        self.name = f"Nlopt optimiser with {self.method} method"
        # this could be the wrong place to do this bit but the optimiser needs to
        # be initialised with parameters and method
        self.opt = nlopt.opt(self.method, optimiser_dims)
        if optimiser_target in ['minimise', 'min', 'minimize']:
            self.minimise = True
            self.maximise = False
        elif optimiser_target == ['maximise', 'max', 'maximize']:
            self.minimise = False
            self.maximise = True

    def _run_optimiser(self, optimisation_problem, x0, bounds):
        self.optimisation_problem = copy.deepcopy(optimisation_problem)
        # Initialise timer
        timer = pybamm.Timer()
        u_bounds = []
        l_bounds = []
        for ix in range(len(bounds)):
            if bounds[ix][0] > bounds[ix][1]:
                u_bounds.append(bounds[ix][0])
                l_bounds.append(bounds[ix][1])
            else:
                u_bounds.append(bounds[ix][1])
                l_bounds.append(bounds[ix][0])

        self.opt.set_lower_bounds(l_bounds)
        self.opt.set_upper_bounds(u_bounds)

        if self.maximise:
            self.opt.set_max_objective(self.optimisation_problem.objective_function)
        elif self.minimise:
            self.opt.set_min_objective(self.optimisation_problem.objective_function)
        else:
            raise ValueError("Must specify whether to maximise or minimise")

        raw_result = self.opt.optimize(x0)
        solve_time = timer.time()

        # Scale the result back to the original scale
        if optimisation_problem.scalings is None:
            scaled_result = raw_result
        else:
            scaled_result = np.multiply(raw_result, optimisation_problem.scalings)
        # Parse the result into a pbparam.OptimisationResult object
        result = pbparam.OptimisationResult(
            scaled_result,
            self.opt.last_optimize_result(),
            raw_result.message,
            self.opt.last_optimum_value(),
            None,
            self.optimisation_problem,
        )
        result.solve_time = solve_time

        return result

