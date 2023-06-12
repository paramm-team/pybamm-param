import pbparam
import pybamm
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

model = pybamm.lithium_ion.SPMe()
parameter_values = pybamm.ParameterValues("Chen2020")

sim0 = pybamm.Simulation(model, parameter_values=parameter_values)
sol = sim0.solve([0, 3600])

V = sol["Voltage [V]"].entries

stds = [1e-1, 5e-2, 1e-2, 5e-3, 1e-3]
results = []
predicted_stds = []

for std in stds:
    data = pd.DataFrame(
        {
            "Time [s]": sol["Time [s]"].entries,
            "Voltage [V]": V + np.random.normal(0, std, size=V.size),
        }
    )

    sim = pybamm.Simulation(model, parameter_values=parameter_values)

    opt = pbparam.DataFit(
        sim,
        data,
        {
            "Negative electrode diffusivity [m2.s-1]": (5e-15, (2.06e-16, 2.06e-12)),
        },
        cost_function=pbparam.MLE(),
    )

    optimiser = pbparam.ScipyDifferentialEvolution(
        extra_options={
            "workers": 4,
            "polish": True,
            "updating": "deferred",
            "disp": True,
        }
    )
    result = optimiser.optimise(opt)
    results.append(result)
    predicted_stds.append(result.x[-1])

plt.plot(stds, stds, "k--")
plt.scatter(stds, predicted_stds)
plt.xlabel("True standard deviation")
plt.ylabel("Predicted standard deviation")
plt.show()
