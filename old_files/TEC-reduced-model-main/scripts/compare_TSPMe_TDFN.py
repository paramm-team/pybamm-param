#
# Comparison between TSPMe and thermal Doyle-Fuller-Newman model
#

import pybamm
import numpy as np
import matplotlib.pyplot as plt
from os import path
from tec_reduced_model.set_parameters import set_thermal_parameters

plt.style.use(["science", "vibrant"])

plt.rcParams.update(
    {
        "font.size": 8,
        "axes.labelsize": 10,
    }
)

pybamm.set_logging_level("INFO")


def compute_error(solutions):
    sol_TSPMe = solutions[0]
    sol_TDFN = solutions[1]
    if sol_TSPMe["Time [s]"].entries[-1] < sol_TDFN["Time [s]"].entries[-1]:
        time = sol_TSPMe["Time [s]"].entries
    else:
        time = sol_TDFN["Time [s]"].entries
    error_V = sol_TSPMe["Terminal voltage [V]"](time) - sol_TDFN[
        "Terminal voltage [V]"
    ](time)
    error_T = sol_TSPMe["X-averaged cell temperature [K]"](time) - sol_TDFN[
        "X-averaged cell temperature [K]"
    ](time)

    error = {}
    error["V"] = error_V
    error["RMSE_V"] = np.sqrt(np.mean(error_V ** 2))
    error["peak_V"] = np.max(np.abs(error_V))
    error["T"] = error_T
    error["RMSE_T"] = np.sqrt(np.mean(error_T ** 2))
    error["peak_T"] = np.max(np.abs(error_T))

    return error


def print_error(error, Crate, temperature, filename=None):
    error_str = (
        "Results for {}C and {}degC\n".format(Crate, temperature)
        + "RMSE V: {:.2f} mV\n".format(error["RMSE_V"] * 1e3)
        + "Peak error V: {:.2f} mV\n".format(error["peak_V"] * 1e3)
        + "RMSE T: {:.2f} °C\n".format(error["RMSE_T"])
        + "Peak error T: {:.2f} °C\n\n".format(error["peak_T"])
    )

    if filename is None:
        print(error_str)
    else:
        with open(filename, "a") as f:
            f.write(error_str)


def add_plot(axes, solutions, error, Crate):
    sol_TSPMe = solutions[0]
    sol_TDFN = solutions[1]
    if sol_TSPMe["Time [s]"].entries[-1] < sol_TDFN["Time [s]"].entries[-1]:
        time = sol_TSPMe["Time [s]"].entries
    else:
        time = sol_TDFN["Time [s]"].entries

    axes[0, 0].plot(
        sol_TDFN["Discharge capacity [A.h]"](time),
        sol_TDFN["Terminal voltage [V]"](time),
        color="black",
        linestyle="dashed",
    )

    axes[0, 0].plot(
        sol_TSPMe["Discharge capacity [A.h]"](time),
        sol_TSPMe["Terminal voltage [V]"](time),
        label="{}C".format(Crate),
    )

    axes[0, 0].set_xlabel("Discharge capacity (Ah)")
    axes[0, 0].set_ylabel("Voltage (V)")
    axes[0, 0].legend(loc="lower left")

    axes[0, 1].plot(
        sol_TDFN["Discharge capacity [A.h]"](time),
        np.abs(error["V"]) * 1e3,
    )
    axes[0, 1].set_xlabel("Discharge capacity (Ah)")
    axes[0, 1].set_ylabel("Voltage error (mV)")

    axes[1, 0].plot(
        sol_TDFN["Discharge capacity [A.h]"](time),
        sol_TDFN["X-averaged cell temperature [K]"](time) - 273.15,
        color="black",
        linestyle="dashed",
    )

    axes[1, 0].plot(
        sol_TSPMe["Discharge capacity [A.h]"](time),
        sol_TSPMe["X-averaged cell temperature [K]"](time) - 273.15,
        label="{}C".format(Crate),
    )

    axes[1, 0].set_xlabel("Discharge capacity (Ah)")
    axes[1, 0].set_ylabel("Temperature (°C)")

    axes[1, 1].plot(
        sol_TDFN["Discharge capacity [A.h]"](time),
        np.abs(error["T"]),
        label="{}C".format(Crate),
    )
    axes[1, 1].set_xlabel("Discharge capacity (Ah)")
    axes[1, 1].set_ylabel("Temperature error (°C)")

    return axes


def compare_models(models, param, Crates, temperature, filename=None):
    fig, axes = plt.subplots(2, 2, figsize=(5.5, 4))

    param["Ambient temperature [K]"] = 273.15 + temperature
    param["Initial temperature [K]"] = 273.15 + temperature

    for Crate in Crates:
        simulations = [None] * len(models)
        solutions = [None] * len(models)

        for i, model in enumerate(models):
            sim = pybamm.Simulation(
                model,
                parameter_values=param,
                C_rate=Crate,
            )
            sim.solve([0, 3700 / Crate])
            solutions[i] = sim.solution
            simulations[i] = sim

        # Compute and print error
        error = compute_error(solutions)
        print_error(error, Crate, temperature, filename=filename)

        # Plot voltage and error
        axes = add_plot(axes, solutions, error, Crate)

    fig.suptitle("Ambient temperature: {} °C".format(temperature))

    fig.tight_layout()
    fig.subplots_adjust(top=0.88)

    return fig


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
# This is the reference parameter set, which will be later adjusted
param = pybamm.ParameterValues(chemistry=pybamm.parameter_sets.Chen2020)

# Change simulation parameters here
temperatures = [0, 10, 25]  # in degC
Crates = [0.5, 1, 2]

root = path.dirname(path.dirname(__file__))

for temperature in temperatures:
    param = set_thermal_parameters(param, 20, 2.85e6, temperature)
    fig = compare_models(
        models, param, Crates, temperature, filename="errors_models.txt"
    )

    fig.savefig(
        path.join(root, "figures", "comp_models_{}degC.png".format(temperature)),
        dpi=300,
    )
