#
# Get computational time for TSPMe and TDFN
#

import pybamm
import numpy as np
from prettytable import PrettyTable

# Import auxiliary functions
from tec_reduced_model.set_parameters import set_thermal_parameters

pybamm.set_logging_level("WARNING")

# Define TSPMe using Integrated electrolyte conductivity submodel
models = [
    pybamm.lithium_ion.SPMe(
        options={
            "thermal": "lumped",
            "dimensionality": 0,
            "cell geometry": "arbitrary",
            "electrolyte conductivity": "integrated",
        },
        name="TSPMe",
    ),
    pybamm.lithium_ion.DFN(
        options={
            "thermal": "lumped",
            "dimensionality": 0,
            "cell geometry": "arbitrary",
        },
        name="TDFN",
    ),
]

# Define parameter set Chen 2020 (see PyBaMM documentation for details)
param = pybamm.ParameterValues(chemistry=pybamm.parameter_sets.Chen2020)

# Change simulation parameters here
N_solve = 20  # number of times to run the solver to get computational time
temperatures = [0, 10, 25]  # in degC
Crates = [0.5, 1, 2]

tables = [PrettyTable([model.name, "C/2", "1C", "2C"]) for model in models]

for i, model in enumerate(models):
    print("Running simulations for", model.name)
    for temperature in temperatures:
        param = set_thermal_parameters(param, 20, 2.85e6, temperature)
        times = [None] * len(Crates)
        for k, Crate in enumerate(Crates):
            print("Running simulation for {}C and {}degC".format(Crate, temperature))
            sim = pybamm.Simulation(
                model,
                parameter_values=param,
                C_rate=Crate,
            )
            time_sublist = []
            for j in range(N_solve):
                sim.solve([0, 3700 / Crate])
                time_sublist.append(sim.solution.solve_time)

            times[k] = time_sublist

        tables[i].add_row(
            ["{}degC".format(temperature)]
            + ["{:.2f} +- {:.2f}".format(np.mean(time), np.std(time)) for time in times]
        )

print()
print("Computational times in seconds:")
for table in tables:
    print()
    print(table)
