
import pybamm
import pbparam
import pandas as pd
import os
os.chdir(os.path.join(pbparam.__path__[0], "input", "data"))

print(os.getcwd())
data = pd.read_csv(os.path.join(os.getcwd(),"C3_1C_profile_25deg.csv"))

print(data)



param = pybamm.ParameterValues("Chen2020") # Initial parameters to be used.
param.update(
    {
        "C1":0.8090,
        "C2":4.4875,
        "C3":0.0428,
        "C4":17.7326,
        "C5":17.5842,
    },
    check_already_exists=False,
)



def nmc_LGM50_ocp_Chen2020(sto):
 
    a= pybamm.Parameter("C1")
    b= pybamm.Parameter("C2")
    c= pybamm.Parameter("C3")
    d= pybamm.Parameter("C4")
    e= pybamm.Parameter("C5")

    # a=0.8090
    # b=4.4875*0.997 #put 0.997
    # c=0.0428*3.25  #put 3.25
    # d=17.7326
    # e=17.5842
  

    u_eq = (
        -a * sto
        + b
        - c * pybamm.tanh(18.5138 * (sto - 0.5542))
        - d * pybamm.tanh(15.7890 * (sto - 0.3117))
        + e* pybamm.tanh(15.9308 * (sto - 0.3120))
    )

    return u_eq


def j0_neg(c_e, c_s_surf, c_s_max, T):

    m_ref = 1.30659051e-06 # pybamm.Parameter("Negative electrode reaction coefficient")
    #m_ref=pybamm.Parameter("Negative electrode reaction coefficient")
    E_r = 3500
    arrhenius = pybamm.exp(E_r / pybamm.constants.R * (1 / 298.15 - 1 / T))
    return (
        m_ref * arrhenius * c_e**0.5 * c_s_surf**0.5 * (c_s_max - c_s_surf) ** 0.5
    )


def j0_pos(c_e, c_s_surf, c_s_max, T):

    m_ref = 3.42e-6  # (A/m2)(m3/mol)**1.5 - includes ref concentrations
    #m_ref=pybamm.Parameter("Positive electrode reaction coefficient")
    E_r = 17800
    arrhenius = pybamm.exp(E_r / pybamm.constants.R * (1 / 298.15 - 1 / T))

    return (
        m_ref * arrhenius * c_e**0.5 * c_s_surf**0.5 * (c_s_max - c_s_surf) ** 0.5
    )
def graphite_LGM50_ocp_Chen2020(sto):

    a=1.9793*1.4
    b=0.2482*0.95
    c=0.0909
    d=0.04478*0.5
    e=0.0205*1.2

    u_eq = (



        a * pybamm.exp(-39.3631 * sto)
        + b
        - c * pybamm.tanh(29.8538 * (sto - 0.1234))
        - d * pybamm.tanh(14.9159 * (sto - 0.2769))
        - e * pybamm.tanh(30.4444 * (sto - 0.6103))
    )

    return u_eq



model = pybamm.lithium_ion.SPMe()

# Update some parameters to match the experimental setup
param.update(
    {
        "Negative electrode diffusivity [m2.s-1]": 2e-14,
        "Initial concentration in positive electrode [mol.m-3]": 17150,
        "Negative electrode exchange-current density [A.m-2]": j0_neg,
        "Positive electrode exchange-current density [A.m-2]": j0_pos,
        "Positive electrode OCP [V]": nmc_LGM50_ocp_Chen2020,
        "Negative electrode OCP [V]": graphite_LGM50_ocp_Chen2020,
        "Negative electrode reaction coefficient": 6.48e-7,
        "Positive electrode reaction coefficient": 3.42e-6,
        "Total heat transfer coefficient [W.m-2.K-1]": 16,
        "Negative electrode diffusivity [m2.s-1]": 3.26522885e-14 ,
        "Positive electrode diffusivity [m2.s-1]": 4.54221604e-15,
        "Ambient temperature [K]": 297.825,
        "Initial temperature [K]": 297.825,
        #"Maximum concentration in negative electrode [mol.m-3]": 33133.0*1.5,
        #"Maximum concentration in positive electrode [mol.m-3]": 63104.0*1.1
    },
    check_already_exists=False,
)


experiment = pybamm.Experiment(
    [
        "Discharge at 4.8 A until 2.5 V",
        "Rest for 1 hours",
        "Charge at 1.6 A until 4.2 V",
        "Hold at 4.2 V until 240 mA",
        "Rest for 30 minutes"
    ],
    period="30 seconds",
)

simulation = pybamm.Simulation(
    model,
    parameter_values=param,
    experiment=experiment,
)



param_optimise = {
    #"Negative electrode diffusivity [m2.s-1]": (5e-14, (2.06e-16, 2.06e-12)),
    #"Positive electrode diffusivity [m2.s-1]": (1e-14, (1e-16, 1e-12)),
    
    #"Maximum concentration in positive electrode [mol.m-3]": (63104.0,(0.9*63104.0,1.1*63104.0)),

     #"C1": (0.8090, (0.1*0.8090, 10*0.8090)),
    # "C2": (4.4875, (0.1*4.4875, 10*4.4875)),
    "C3": (0.0428, (0.1*0.0428, 10*0.0428)),
    # "C4": (17.7326, (0.1*17.7326, 10*17.7326)),
    # "C5": (17.5842, (0.1*17.5842, 10*17.5842)),
    #"Negative electrode reaction coefficient": ( 6.48e-7,(2.18589831e-9, 2.18589831e-5)),
    #"Positive electrode reaction coefficient": (3.42e-6, (1.2e-9, 1.2e-4)),
}


variables_optimise = ["Voltage [V]"]

cost_function = pbparam.RMSE()
# Since this is a parameter optimisation with fitting data into experimental data, optimisation problem is DataFit.
opt = pbparam.DataFit(simulation, data, param_optimise, variables_optimise, cost_function,solve_options={"calc_esoh": False})

# optimiser = pbparam.ScipyDifferentialEvolution(
#     extra_options={"workers": 4, "polish": True, "updating": "deferred", "disp": True}
# )
optimiser = pbparam.ScipyMinimize(method="Nelder-Mead")

result = optimiser.optimise(opt)
# optimised values of parameters and function values can be printed as below.
print(result)

result.plot()
