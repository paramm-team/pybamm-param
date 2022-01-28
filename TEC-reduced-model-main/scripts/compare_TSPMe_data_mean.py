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
from scipy.interpolate import interp1d

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
    voltage_fun = {}
    temperature_fun = {}

    t_end = 0

    for cell, data in dataset.items():
        if cell in cells_ignore:
            continue

        idx_start, idx_end = get_idxs(data, Crate * 5, 5 / 3)
        if len(idx_end) == 1:
            idx_end = np.append(idx_end, len(data["Time [s]"]))

        t_end = max(
            t_end, data["Time [s]"][idx_end[1] - 1] - data["Time [s]"][idx_start[0]]
        )

        if data["Time [s]"][idx_start[0]] == data["Time [s]"][idx_start[0] + 1]:
            data.drop([idx_start[0] + 1], inplace=True)

        voltage_fun.update(
            {
                cell: interp1d(
                    data["Time [s]"][idx_start[0] : idx_end[1]]
                    - data["Time [s]"][idx_start[0]],
                    data["Voltage [V]"][idx_start[0] : idx_end[1]],
                    fill_value="extrapolate",
                )
            }
        )
        temperature_fun.update(
            {
                cell: interp1d(
                    data["Time [s]"][idx_start[0] : idx_end[1]]
                    - data["Time [s]"][idx_start[0]],
                    data["Temp Cell [degC]"][idx_start[0] : idx_end[1]],
                    fill_value="extrapolate",
                )
            }
        )

    t_eval = np.linspace(0, t_end, num=1000)

    voltage_data = []
    temperature_data = []

    for cell, V in voltage_fun.items():
        V = voltage_fun[cell]
        T = temperature_fun[cell]

        voltage_data.append(V(t_eval))
        temperature_data.append(T(t_eval))

    V_mean = np.mean(np.array(voltage_data), axis=0)
    V_std = np.std(np.array(voltage_data), axis=0)
    T_mean = np.mean(np.array(temperature_data), axis=0)
    T_std = np.std(np.array(temperature_data), axis=0)

    axes[0].fill_between(
        t_eval,
        V_mean - V_std,
        V_mean + V_std,
        alpha=0.2,
    )
    axes[0].plot(t_eval, V_mean, label="data")
    axes[1].fill_between(
        t_eval,
        T_mean - T_std,
        T_mean + T_std,
        alpha=0.2,
    )
    axes[1].plot(t_eval, T_mean, label="data")
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

    return axes, {}


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

    if Crate == 0.5:
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

        axes[k, :], _ = plot_experimental_data(
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

    fig.suptitle("Ambient temperature: {} °C".format(temperature))

    fig.tight_layout()
    fig.subplots_adjust(left=0.15, top=0.92)

    return fig


# Define models
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
    )

    fig.savefig(
        path.join(root, "figures", "comp_exp_{}degC_mean.png".format(temperature)),
        dpi=300,
    )
