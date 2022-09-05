import os
import process_experimental_data as prepos
from set_parameters import (
    set_thermal_parameters,
    set_experiment_parameters,
    set_ambient_temperature,
)
import pybamm
import numpy as np
import pbparam
import pandas as pd
os.chdir("../..")

temperature = 25  # in degC, valid values: 0, 10, 25
crate = 1  # valid values: 0.5, 1, 2
cell_selected = ["789"]
dataset = prepos.import_thermal_data(crate, temperature)
data_conc = {
    "Time [s]": [],
    "Terminal voltage [V]": [],
    "X-averaged cell temperature [degC]": [],
}
for cell, data in dataset.items():
    if cell in cell_selected:
        idx_start, idx_end = prepos.get_idxs(data, crate * 5, 5 / 3)
        if len(idx_end) == 1:
            idx_end = np.append(idx_end, len(data["Time [s]"]))
        data_conc["Time [s]"] = np.append(
            data_conc["Time [s]"],
            data["Time [s]"][idx_start[0] : idx_end[1]]
            - data["Time [s]"][idx_start[0]],
        )
        data_conc["Terminal voltage [V]"] = np.append(
            data_conc["Terminal voltage [V]"],
            data["Voltage [V]"][idx_start[0] : idx_end[1]],
        )
        data_conc["X-averaged cell temperature [degC]"] = np.append(
            data_conc["X-averaged cell temperature [degC]"],
            data["Temp Cell [degC]"][idx_start[0] : idx_end[1]],
        )
data_conc = pd.DataFrame(data_conc)
data_conc["X-averaged cell temperature [degC]"] = (
    data_conc["X-averaged cell temperature [degC]"] + 273.15
)
data_conc = data_conc.rename(
    columns={"X-averaged cell temperature [degC]": "X-averaged cell temperature [K]"}
)


def j0_neg(c_e, c_s_surf, T):
    """
    This function has been copied from the Chen2020 parameter set:
    pybamm/input/parameters/lithium_ion/negative_electrodes/graphite_Chen2020
    /graphite_LGM50_electrolyte_exchange_current_density_Chen2020.py
    Similar could be done for the positive exchange current density
    """
    m_ref = pybamm.Parameter("Negative electrode reaction coefficient")
    E_r = 3500
    arrhenius = pybamm.exp(E_r / pybamm.constants.R * (1 / 298.15 - 1 / T))
    c_n_max = pybamm.Parameter("Maximum concentration in negative electrode [mol.m-3]")
    return (
        m_ref * arrhenius * c_e**0.5 * c_s_surf**0.5 * (c_n_max - c_s_surf) ** 0.5
    )


model = pybamm.lithium_ion.SPMe(
    options={
        "thermal": "lumped",
        "dimensionality": 0,
        "cell geometry": "arbitrary",
        "electrolyte conductivity": "integrated",
    },
    name="TSPMe",
)

param_default = pybamm.ParameterValues(chemistry=pybamm.parameter_sets.Chen2020)
param = set_thermal_parameters(param_default, 16, 2.32e6, temperature)
param = set_experiment_parameters(param, crate, temperature)
param = set_ambient_temperature(param, crate, temperature)
param.update(
    {
        "Negative electrode exchange-current density [A.m-2]": j0_neg,
        "Negative electrode reaction coefficient": 6.48e-7
        # "Negative electrode diffusivity [m2.s-1]" : "[input]",
        # "Total heat transfer coefficient [W.m-2.K-1]" : "[input]",
        # "Positive current collector specific heat capacity [J.kg-1.K-1]" : "[input]",
        # "Negative current collector specific heat capacity [J.kg-1.K-1]" : "[input]",
        # "Negative electrode specific heat capacity [J.kg-1.K-1]" : "[input]",
        # "Separator specific heat capacity [J.kg-1.K-1]" : "[input]",
        # "Positive electrode specific heat capacity [J.kg-1.K-1]" : "[input]"
    },
    check_already_exists=False,
)
experiment = pybamm.Experiment(
    [
        "Discharge at {}C until 2.5 V (5 seconds period)".format(crate),
        "Rest for 2 hours",
    ],
    period="30 seconds",
)
simulation = pybamm.Simulation(
    model,
    parameter_values=param,
    experiment=experiment,
)
param_optimised = {
    "Negative electrode diffusivity [m2.s-1]": (5e-14, (2.06e-16, 2.06e-12)),
    "Negative electrode reaction coefficient": (
        6.48e-7,
        (2.18589831e-9, 2.18589831e-5),
    ),
    "Total heat transfer coefficient [W.m-2.K-1]": (20, (0.1, 1000)),
    (
        "Positive current collector specific heat capacity [J.kg-1.K-1]",
        "Negative current collector specific heat capacity [J.kg-1.K-1]",
        "Negative electrode specific heat capacity [J.kg-1.K-1]",
        "Separator specific heat capacity [J.kg-1.K-1]",
        "Positive electrode specific heat capacity [J.kg-1.K-1]",
    ): (2.85e3, (2.85, 2.85e6)),
}
variables_optimised = ["Terminal voltage [V]", "X-averaged cell temperature [K]"]
opt = pbparam.DataFit(simulation, data_conc, param_optimised, variables_optimised)
optimiser = pbparam.ScipyDifferentialEvolution(
    extra_options={"workers": 1, "polish": True, "updating": "deferred", "disp": True}
)
result = optimiser.optimise(opt)
result.plot()
