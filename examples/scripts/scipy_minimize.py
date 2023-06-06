import pbparam
import pybamm
import pandas as pd

model = pybamm.lithium_ion.SPMe()
parameter_values = pybamm.ParameterValues("Chen2020")

sim0 = pybamm.Simulation(model, parameter_values=parameter_values)
sol = sim0.solve([0, 3600])

data = pd.DataFrame(
    {
        "Time [s]": sol["Time [s]"].entries,
        "Voltage [V]": sol["Voltage [V]"].entries,
    }
)

sim = pybamm.Simulation(model, parameter_values=parameter_values)

opt = pbparam.DataFit(
    sim,
    data,
    {
        "Negative electrode diffusivity [m2.s-1]": (5e-15, (2.06e-16, 2.06e-12)),
        # "Total heat transfer coefficient [W.m-2.K-1]": (20, (0.1, 1000)),
        # (
        #     "Positive current collector specific heat capacity [J.kg-1.K-1]",
        #     "Negative current collector specific heat capacity [J.kg-1.K-1]",
        #     "Negative electrode specific heat capacity [J.kg-1.K-1]",
        #     "Separator specific heat capacity [J.kg-1.K-1]",
        #     "Positive electrode specific heat capacity [J.kg-1.K-1]",
        # ): (2.85e3, (2.85, 2.85e6)),
    },
)

optimiser = pbparam.ScipyMinimize(method="Nelder-Mead", extra_options={"tol": 1e-6})

result = optimiser.optimise(opt)

print(result)

result.plot()
