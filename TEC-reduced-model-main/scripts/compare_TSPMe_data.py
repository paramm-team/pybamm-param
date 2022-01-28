#
# Comparison between TSPMe and experimental data
#

import pybamm
import numpy as np
import matplotlib.pyplot as plt
from os import path
from tec_reduced_model.set_parameters import (
    set_thermal_parameters,
    set_experiment_parameters,
    set_ambient_temperature,
)
from tec_reduced_model.process_experimental_data import import_thermal_data, get_idxs

plt.style.use(["science", "vibrant"])

plt.rcParams.update(
    {
        "font.size": 8,
        "axes.labelsize": 10,
    }
)

pybamm.set_logging_level("INFO")


def rmse(solution, x_data, y_data):
    error = solution(x_data) - y_data
    error = error[~np.isnan(error)]  # remove NaNs due to extrapolation
    return np.sqrt(np.mean(error ** 2))


def R_squared(solution, x_data, y_data):
    y_bar = np.mean(y_data)
    SS_tot = np.sum((y_data - y_bar) ** 2)
    res = y_data - solution(x_data)
    res = res[~np.isnan(res)]  # remove NaNs due to extrapolation
    SS_res = np.sum(res ** 2)

    return 1 - SS_res / SS_tot


def compute_error(solution, data_conc):
    error = {}
    error["RMSE_V"] = rmse(
        solution["Terminal voltage [V]"], data_conc["time"], data_conc["voltage"]
    )
    error["Rsq_V"] = R_squared(
        solution["Terminal voltage [V]"], data_conc["time"], data_conc["voltage"]
    )
    error["RMSE_T"] = rmse(
        solution["X-averaged cell temperature [K]"],
        data_conc["time"],
        data_conc["temperature"] + 273.15,
    )
    error["Rsq_T"] = R_squared(
        solution["X-averaged cell temperature [K]"],
        data_conc["time"],
        data_conc["temperature"] + 273.15,
    )

    return error


def print_error(error, Crate, temperature, filename=None):
    error_str = (
        "Results for {}C and {}degC\n".format(Crate, temperature)
        + "RMSE V: {:.2f} mV\n".format(error["RMSE_V"] * 1e3)
        + "R^2 V: {:.2f}\n".format(error["Rsq_V"])
        + "RMSE T: {:.2f} °C\n".format(error["RMSE_T"])
        + "R^2 T: {:.2f} \n\n".format(error["Rsq_T"])
    )

    if filename is None:
        print(error_str)
    else:
        with open(filename, "a") as f:
            f.write(error_str)


def plot_experimental_data(axes, Crate, temperature, cells_ignore):
    dataset = import_thermal_data(Crate, temperature)
    data_conc = {"time": [], "voltage": [], "temperature": []}

    for cell, data in dataset.items():
        if cell in cells_ignore:
            continue

        idx_start, idx_end = get_idxs(data, Crate * 5, 5 / 3)
        if len(idx_end) == 1:
            idx_end = np.append(idx_end, len(data["Time [s]"]))
        axes[0].plot(
            data["Time [s]"][idx_start[0] : idx_end[1]]
            - data["Time [s]"][idx_start[0]],
            data["Voltage [V]"][idx_start[0] : idx_end[1]],
            label=cell,
            linewidth=1,
            ls="--",
        )
        axes[1].plot(
            data["Time [s]"][idx_start[0] : idx_end[1]]
            - data["Time [s]"][idx_start[0]],
            data["Temp Cell [degC]"][idx_start[0] : idx_end[1]],
            label=cell,
            linewidth=1,
            ls="--",
        )
        pad = 4

        axes[0].annotate(
            "{}C".format(Crate),
            xy=(0, 0.5),
            xytext=(-axes[0].yaxis.labelpad - pad, 0),
            xycoords=axes[0].yaxis.label,
            textcoords="offset points",
            size="large",
            ha="right",
            va="center",
        )

        data_conc["time"] = np.append(
            data_conc["time"],
            data["Time [s]"][idx_start[0] : idx_end[1]]
            - data["Time [s]"][idx_start[0]],
        )
        data_conc["voltage"] = np.append(
            data_conc["voltage"], data["Voltage [V]"][idx_start[0] : idx_end[1]]
        )
        data_conc["temperature"] = np.append(
            data_conc["temperature"],
            data["Temp Cell [degC]"][idx_start[0] : idx_end[1]],
        )

    return axes, data_conc


def plot_model_solutions(axes, solution, Crate, temperature):
    if solution.model.name == "TSPMe":
        ls = "-"
        color = "black"
        linewidth = 0.75
    else:
        ls = ":"
        color = "gray"
        linewidth = 1

    axes[0].plot(
        solution["Time [s]"].entries,
        solution["Terminal voltage [V]"].entries,
        color=color,
        label=solution.model.name,
        ls=ls,
        linewidth=linewidth,
    )

    if solution.model.name == "TSPMe":
        axes[0].scatter(
            0,
            solution["X-averaged battery open circuit voltage [V]"].entries[0],
            s=15,
            marker="x",
            color="black",
            linewidths=0.75,
        )

    axes[0].set_xlabel("Time (s)")
    axes[0].set_ylabel("Voltage (V)")

    axes[1].plot(
        solution["Time [s]"].entries,
        solution["X-averaged cell temperature [K]"].entries - 273.15,
        color=color,
        label=solution.model.name,
        ls=ls,
        linewidth=linewidth,
    )

    axes[1].set_xlabel("Time (s)")
    axes[1].set_ylabel("Cell temperature (°C)")
    axes[1].legend()

    if temperature == 25 and Crate == 1:
        axes[1].set_yticks([25, 28, 31, 34, 37])

    return axes


def compare_data(models, param, Crates, temperature, cells_ignore=None, filename=None):
    fig, axes = plt.subplots(3, 2, figsize=(5.7, 5.5))

    for k, Crate in enumerate(Crates):
        param = set_experiment_parameters(param, Crate, temperature)
        param = set_ambient_temperature(param, Crate, temperature)

        experiment = pybamm.Experiment(
            [
                "Discharge at {}C until 2.5 V (5 seconds period)".format(Crate),
                "Rest for 2 hours",
            ],
            period="30 seconds",
        )

        solutions = []

        axes[k, :], data_conc = plot_experimental_data(
            axes[k, :], Crate, temperature, cells_ignore
        )

        for model in models:
            simulation = pybamm.Simulation(
                model,
                parameter_values=param,
                experiment=experiment,
            )
            simulation.solve()
            solution = simulation.solution
            solutions.append(solution)

            axes[k, :] = plot_model_solutions(axes[k, :], solution, Crate, temperature)
            error = compute_error(solution, data_conc)
            idx = filename.index(".")
            new_filename = filename[:idx] + "_" + model.name + filename[idx:]
            print_error(error, Crate, temperature, filename=new_filename)

    fig.suptitle("Ambient temperature: {} °C".format(temperature))

    fig.tight_layout()
    fig.subplots_adjust(left=0.15, top=0.92)

    return fig


# Define models
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
cells_ignore = ["791"]

root = path.dirname(path.dirname(__file__))

for temperature in temperatures:
    param = set_thermal_parameters(param, 16, 2.32e6, temperature)
    fig = compare_data(
        models,
        param,
        Crates,
        temperature,
        cells_ignore=cells_ignore,
        filename="errors_experiments.txt",
    )

    fig.savefig(
        path.join(root, "figures", "comp_exp_{}degC.png".format(temperature)),
        dpi=300,
    )
