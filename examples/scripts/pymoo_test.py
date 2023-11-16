#%pip install git+https://github.com/paramm-team/pybamm-param.git -q
import pybamm
import pbparam
import pandas as pd

syn_model = pybamm.lithium_ion.SPM()

syn_param = pybamm.ParameterValues("Chen2020")

# Use a linearised OCP to check model is working
def linear_OCP(sto):
    return 4.2935 - 1.1352 * (sto - 0.2661)

syn_param.update(
            {
                "Positive electrode OCP [V]": linear_OCP,
                "Positive electrode diffusivity [m2.s-1]": 1e-15,
            },
            check_already_exists=True,
)

syn_sim = pybamm.Simulation(syn_model, parameter_values=syn_param)
syn_solution = syn_sim.solve([0, 100])


d = {'Time [s]':syn_solution["Time [s]"].entries, 'Voltage [V]': syn_solution["Voltage [V]"].entries}

data = pd.DataFrame(data = d)

model = pbparam.WeppnerHuggins()

param_dict = pybamm.ParameterValues({
        "Reference OCP [V]": 4.0,
        "Derivative of the OCP wrt stoichiometry [V]": -1.1352,
        "Current function [A]": syn_param["Current function [A]"],
        "Number of electrodes connected in parallel to make a cell": \
            syn_param["Number of electrodes connected in parallel to make a cell"],
        "Electrode width [m]": syn_param["Electrode width [m]"],
        "Electrode height [m]": syn_param["Electrode height [m]"],
        "Positive electrode active material volume fraction": \
            syn_param["Positive electrode active material volume fraction"],
        "Positive particle radius [m]": syn_param["Positive particle radius [m]"],
        "Positive electrode thickness [m]": \
            syn_param["Positive electrode thickness [m]"],
        "Positive electrode diffusivity [m2.s-1]": \
            syn_param["Positive electrode diffusivity [m2.s-1]"],
        "Maximum concentration in positive electrode [mol.m-3]": \
            syn_param["Maximum concentration in positive electrode [mol.m-3]"],
})

# optimisation problem is GITT.
opt = pbparam.GITT(param_dict=param_dict, gitt_model=model, data=data)

optimiser = pbparam.PymooMinimize()

result = optimiser.optimise(opt)

result.plot()