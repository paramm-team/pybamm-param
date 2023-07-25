import os
import pybamm
import pbparam
import pandas as pd

# Change working directory to import data
os.chdir(
    os.path.join(
        pbparam.__path__[0],
        "input",
        "data",
    )
)

data = pd.read_csv("LGM50_789_1C_25degC.csv")


def j0_neg(c_e, c_s_surf, c_s_max, T):
    """
    This function has been copied from the Chen2020 parameter set:
    pybamm/input/parameters/lithium_ion/negative_electrodes/graphite_Chen2020
    /graphite_LGM50_electrolyte_exchange_current_density_Chen2020.py
    Similar could be done for the positive exchange current density
    """
    m_ref = pybamm.Parameter("Negative electrode reaction coefficient")
    E_r = 3500
    arrhenius = pybamm.exp(E_r / pybamm.constants.R * (1 / 298.15 - 1 / T))
    return (
        m_ref * arrhenius * c_e**0.5 * c_s_surf**0.5 * (c_s_max - c_s_surf) ** 0.5
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

param = pybamm.ParameterValues("Chen2020")
param.update(
    {
        "Negative electrode exchange-current density [A.m-2]": j0_neg,
        "Negative electrode reaction coefficient": 6.48e-7,
    },
    check_already_exists=False,
)
experiment = pybamm.Experiment(
    [
        "Discharge at 1C until 2.5 V (5 seconds period)",
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
    # "Negative electrode reaction coefficient": (
    #     6.48e-7,
    #     (2.18589831e-9, 2.18589831e-5),
    # ),
    "Total heat transfer coefficient [W.m-2.K-1]": (20, (0.1, 1000)),
    # (
    #     "Positive current collector specific heat capacity [J.kg-1.K-1]",
    #     "Negative current collector specific heat capacity [J.kg-1.K-1]",
    #     "Negative electrode specific heat capacity [J.kg-1.K-1]",
    #     "Separator specific heat capacity [J.kg-1.K-1]",
    #     "Positive electrode specific heat capacity [J.kg-1.K-1]",
    # ): (2.85e3, (2.85, 2.85e6)),
}
variables_optimised = ["Voltage [V]", "X-averaged cell temperature [K]"]
opt = pbparam.DataFit(simulation, data, param_optimised, variables_optimised)
optimiser = pbparam.ScipyMinimize(method="Nelder-Mead")
result = optimiser.optimise(opt)

print(result)
result.plot()
