#
# This is a minimal example based on the original suggestion to use NLOpt
# We make a simple dummy optimisation class for easier debugging
#

import pybamm
import numpy as np
import pbparam

model = pybamm.lithium_ion.SPM()
parameter_values = pybamm.ParameterValues("Chen2020")
parameter_values.update(
    {"Current function [A]": pybamm.InputParameter("I")}
)
sim = pybamm.Simulation(model, parameter_values=parameter_values)
sol = sim.solve([0, 3600], inputs={"I": 5})["Terminal voltage [V]"].data


# Turn this into a mini optimisation problem
class MyOptimisationProblem():
    def __init__(self, x0, bounds):
        self.x0 = x0
        self.bounds = bounds
        self.scalings = None

    def objective_function(self, x):
        output = 2.5 * np.ones(100)
        new_sol = sim.solve([0, 3600], inputs={"I": x[0]})["Terminal voltage [V]"].data
        output[:len(new_sol)] = new_sol
        return sum((output - sol) ** 2)

    def setup_objective_function(self):
        pass


# The init method takes the following 3 lines
opt_class = pbparam.Nlopt('LN_BOBYQA', 'minimise')


# 3 lines handled in init
#opt = nlopt.opt(nlopt.LN_BOBYQA, 1)
#opt = nlopt.opt('LN_BOBYQA', 1)
#opt.set_xtol_rel(1e-4)

# the opt problem is set up in the optimise method using one of the extentions to
# pbparam.base_optimisation_problem
opt = MyOptimisationProblem([5], [(0, 10)])


result = opt_class.optimise(opt)


print(result)
