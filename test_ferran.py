import pybamm
import pandas as pd
from optimisation_problem import OptimisationProblem

model = pybamm.lithium_ion.SPMe()
parameter_values = pybamm.ParameterValues("Chen2020")

sim0 = pybamm.Simulation(model, parameter_values=parameter_values)
sol = sim0.solve([0, 3600])

data = pd.DataFrame(
    {
        "Time [s]": sol["Time [s]"].entries,
        "Terminal voltage [V]": sol["Terminal voltage [V]"].entries,
    }
)

parameter_values["Negative electrode diffusivity [m2.s-1]"] = "[input]"
sim = pybamm.Simulation(model, parameter_values=parameter_values)

opt = OptimisationProblem(
    sim,
    data,
    {
        "Negative electrode diffusivity [m2.s-1]": (5e-14, (2.06e-16, 2.06e-12)),
        "Total heat transfer coefficient [W.m-2.K-1]": (20, (0.1, 1000)),
        (
            "Positive current collector specific heat capacity [J.kg-1.K-1]",
            "Negative current collector specific heat capacity [J.kg-1.K-1]",
            "Negative electrode specific heat capacity [J.kg-1.K-1]",
            "Separator specific heat capacity [J.kg-1.K-1]",
            "Positive electrode specific heat capacity [J.kg-1.K-1]",
        ): (2.85e3, (2.85, 2.85e6)),
    },
)

x0 = [3.3e-14, 20, 2.85e3]

opt.define_cost_function()

print(opt.cost_function(x0))

2 + 2
