import pybamm
import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd
from tec_reduced_model.set_parameters import (
    set_thermal_parameters,
    set_experiment_parameters,
    set_ambient_temperature,
)
#Import all the required packages
#from tec_reduced_model.process_experimental_data import import_thermal_data, get_idxs
#from __future__ import print_function
plt.style.use(['science','vibrant'])

plt.rcParams.update({
    "font.family": "sans-serif",
    "text.usetex": False,
    "font.size": 8,
    "axes.labelsize": 10,
})

class model_build:  #build class first for PyBamm model
    
    def __init__(self, temperature, crate, cell_selected):  #In the model_build temperature, crate and selected cell should be defined
    
        self.globals = {'temperature':temperature, 'crate':crate, 'cell_selected':cell_selected}
        
   # def define_model(self):
        global simulation, data_conc, param     #make simulation, data_conc and param glabal to use pybamm model in init
        temperature=self.globals["temperature"]
        crate = self.globals["crate"]
        cell_selected = self.globals["cell_selected"]
        
            # Define the TSPMe model
        model = pybamm.lithium_ion.SPMe(
            options={
                "thermal": "lumped",
                "dimensionality": 0,
                "cell geometry": "arbitrary",
                "electrolyte conductivity": "integrated",
             },
             name="TSPMe",
        )
    
        dataset = import_thermal_data(crate, temperature) #Import test data 
        data_conc = {"time": [], "voltage": [], "temperature": []}
        
        #store real-world test data in data_conc with time, temeperature and voltage
        for cell, data in dataset.items():
            if cell in cell_selected:
#                continue

                idx_start, idx_end = get_idxs(data, crate * 5, 5 / 3)
                if len(idx_end) == 1:
                    idx_end = np.append(idx_end, len(data["Time [s]"]))

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
        # Define parameter set Chen 2020 (see PyBaMM documentation for details)
        # This is the reference parameter set, which we then update for the adjusted thermal parameters
        param = pybamm.ParameterValues(chemistry=pybamm.parameter_sets.Chen2020)
        # We now update the parameter set for the adjusted parameters
        param = set_thermal_parameters(param, 16, 2.32e6, temperature)
        param = set_experiment_parameters(param, crate, temperature)
        param = set_ambient_temperature(param, crate, temperature)
    
        # Define the experiment to be a CC discharge at the defined C-rate followed by a 2-hour relaxation
        experiment = pybamm.Experiment(
            [
                "Discharge at {}C until 2.5 V (5 seconds period)".format(crate),
                "Rest for 2 hours",
            ],
            period="30 seconds",
        )
        #Define the parameters to be optimized
        param.update({
            "Negative electrode exchange-current density [A.m-2]": j0_neg,
            "Negative electrode reaction coefficient": "[input]",
            "Negative electrode diffusivity [m2.s-1]" : "[input]",
            "Total heat transfer coefficient [W.m-2.K-1]" : "[input]",
            "Positive current collector specific heat capacity [J.kg-1.K-1]" : "[input]",
            "Negative current collector specific heat capacity [J.kg-1.K-1]" : "[input]",
            "Negative electrode specific heat capacity [J.kg-1.K-1]" : "[input]",
            "Separator specific heat capacity [J.kg-1.K-1]" : "[input]",
            "Positive electrode specific heat capacity [J.kg-1.K-1]" : "[input]"
        }, check_already_exists=False)
    
        # Solve the model
        simulation = pybamm.Simulation(
            model,
            parameter_values=param,
            experiment=experiment,
            )
        
        #return (simulation, data_conc)
        
        #Define the optimization function. This function will be minimized by an external algorithm.
    def fitness(self,x):
        #model=model_build(self.globals["temperature"],self.globals["crate"],self.globals["cell"])
        #simulation, data_conc = model.define_model()

        #Define the parameters with x[k]
        simulation.solve(inputs={"Negative electrode diffusivity [m2.s-1]" : x[0],
                                 "Negative electrode reaction coefficient": x[1],
                                 "Total heat transfer coefficient [W.m-2.K-1]":x[2],
                                 "Positive current collector specific heat capacity [J.kg-1.K-1]":x[3],
                                 "Negative current collector specific heat capacity [J.kg-1.K-1]":x[3],
                                 "Negative electrode specific heat capacity [J.kg-1.K-1]":x[3],
                                 "Separator specific heat capacity [J.kg-1.K-1]":x[3],
                                 "Positive electrode specific heat capacity [J.kg-1.K-1]":x[3]
                                })
        solution = simulation.solution
        
        #temperature and voltage cost functions defined here. R_squared function in the auxiliary functions is used.
        # Then they are normalized to get equal effect on the cost function. Sum of normalized functions returned. This sum could be minimized.
        temp_r_squared=1-R_squared(solution["X-averaged cell temperature [K]"], data_conc["time"], (data_conc["temperature"] + 273.15))
        volt_r_squared=1-R_squared(solution["Terminal voltage [V]"], data_conc["time"], data_conc["voltage"])
        temp_normalized=temp_r_squared/(np.average(data_conc["temperature"]+273.15))
        volt_normalized=volt_r_squared/(np.average(data_conc["voltage"]))
                      
        return np.array(temp_normalized+volt_normalized) 
    
        # Defining the new PyBamm model with optimized parameters
    def define_model(self, minimum):
         #self.globals = {'minimum':minimum}
            # Define the TSPMe model
        crate=self.globals["crate"]
        temperature=self.globals["temperature"]
        cell_selected = self.globals["cell_selected"]
        global solution, solution_chen
        model = pybamm.lithium_ion.SPMe(
            options={
                "thermal": "lumped",
                "dimensionality": 0,
                "cell geometry": "arbitrary",
                "electrolyte conductivity": "integrated",
            },
            name="TSPMe",
        )

        # Define parameter set Chen 2020 (see PyBaMM documentation for details)
        # This is the reference parameter set, which we then update for the adjusted thermal parameters
        param_chen = pybamm.ParameterValues(chemistry=pybamm.parameter_sets.Chen2020)
        # We now update the parameter set for the adjusted parameters
        param_chen = set_thermal_parameters(param_chen, 16, 2.32e6, temperature)
        param_chen = set_experiment_parameters(param_chen, crate, temperature)
        param_chen = set_ambient_temperature(param_chen, crate, temperature)

# Define the experiment to be a CC discharge at the defined C-rate followed by a 2-hour relaxation
        experiment = pybamm.Experiment(
            [
                "Discharge at {}C until 2.5 V (5 seconds period)".format(crate),
                "Rest for 2 hours",
            ],
            period="30 seconds",
        )

        # Solve the model
        simulation_chen = pybamm.Simulation(
            model,
            parameter_values=param_chen,
            experiment=experiment,
        )
        simulation_chen.solve()
        solution_chen = simulation_chen.solution
        
        # Solve the model
        
        simulation = pybamm.Simulation(
            model,
            parameter_values=param,
            experiment=experiment,
        )
        simulation.solve( inputs={"Negative electrode diffusivity [m2.s-1]":minimum[0],
                                  "Negative electrode reaction coefficient": minimum[1],
                                  "Total heat transfer coefficient [W.m-2.K-1]":minimum[2],
                                  "Positive current collector specific heat capacity [J.kg-1.K-1]":minimum[3],
                                  "Negative current collector specific heat capacity [J.kg-1.K-1]":minimum[3],
                                  "Negative electrode specific heat capacity [J.kg-1.K-1]":minimum[3],
                                  "Separator specific heat capacity [J.kg-1.K-1]":minimum[3],
                                  "Positive electrode specific heat capacity [J.kg-1.K-1]":minimum[3]
                                 })
        solution = simulation.solution

    def model_plot(self):
        temperature=self.globals["temperature"]
        crate = self.globals["crate"]
        cell_selected = self.globals["cell_selected"]
        
        fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
        dataset = import_thermal_data(crate, temperature)
        data_conc = {"time": [], "voltage": [], "temperature": []}
    
        for cell, data in dataset.items():
            if cell in cell_selected:
                idx_start, idx_end = get_idxs(data, crate * 5, 5 / 3)
                if len(idx_end) == 1:
                    idx_end = np.append(idx_end, len(data["Time [s]"]))
            
                axes[0].plot(
                    data["Time [s]"][idx_start[0] : idx_end[1]]
                    - data["Time [s]"][idx_start[0]],
                    data["Voltage [V]"][idx_start[0] : idx_end[1]],
                    label=cell,
                )
                axes[1].plot(
                    data["Time [s]"][idx_start[0] : idx_end[1]]
                    - data["Time [s]"][idx_start[0]],
                    data["Temp Cell [degC]"][idx_start[0] : idx_end[1]],
                    label=cell,
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

    
                axes[0].plot(
                    solution["Time [s]"].entries,
                    solution["Terminal voltage [V]"].entries,
                    color="black",
                    label="TSPMe",
                )
                
                axes[0].plot(
                    solution_chen["Time [s]"].entries,
                    solution_chen["Terminal voltage [V]"].entries,
                    'r--',
                    label="Chen(2020)",
                )
    
                axes[0].scatter(
                    0,
                    solution["X-averaged battery open circuit voltage [V]"].entries[0],
                    marker="x",
                    color="black"
                )
                axes[0].scatter(
                    0,
                    solution_chen["X-averaged battery open circuit voltage [V]"].entries[0]
                )

                axes[0].set_xlabel("Time (s)")
                axes[0].set_ylabel("Voltage (V)")
    
                axes[1].plot(
                    solution["Time [s]"].entries,
                    solution["X-averaged cell temperature [K]"].entries - 273.15,
                    color="black",
                    label="TSPMe",
                )
                axes[1].plot(
                    solution_chen["Time [s]"].entries,
                    solution_chen["X-averaged cell temperature [K]"].entries - 273.15,
                    'r--',
                    label="Chen(2020)",
                )
    
                axes[1].set_xlabel("Time (s)")
                axes[1].set_ylabel("Cell temperature (°C)")
                axes[1].legend()
    
                fig.suptitle("Ambient temperature: {} °C, C-rate: {}C".format(temperature, crate))    
    
                fig.tight_layout()
                fig.subplots_adjust(top=0.9)
        
        
#Auxiliary functions

def R_squared(solution, x_data, y_data):
    y_bar = np.mean(y_data)
    SS_tot = np.sum((y_data - y_bar) ** 2)
    res = y_data - solution(x_data)
    res = res[~np.isnan(res)]  # remove NaNs due to extrapolation
    SS_res = np.sum(res ** 2)
    n=len(y_data)
    return 1 - SS_res / n
    
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
    return (m_ref * arrhenius * c_e ** 0.5 * c_s_surf ** 0.5 * (c_n_max - c_s_surf) ** 0.5)

def get_idxs(data, I_dch, I_ch):
    i = data["Current [A]"]
    diff_i = np.diff(i)
    idx_start = np.where((diff_i < 0.95 * (-I_dch)) & (diff_i > 1.05 * (-I_dch)))
    idx_end = np.where((diff_i > 0.95 * I_ch) & (diff_i < 1.05 * I_ch))
    return idx_start[0], idx_end[0]

def import_thermal_data(Crate, T):
    if Crate == 0.1:
        cells = ["781", "782", "783", "784"]
    elif Crate == 0.5:
        cells = ["785", "786", "787", "788"]
    elif Crate == 1:
        cells = ["789", "790", "791", "792"]
    elif Crate == 2:
        cells = ["793", "794", "795", "796"]
    else:
        raise ValueError("Invalid C-rate")

    if T not in [0, 10, 25]:
        raise ValueError("Invalid temperature value")

    datasets = {}
    skiprows = list(range(15))
    skiprows.append(16)

    root = os.path.dirname(os.path.dirname(__file__))
    folder = "{}degC".format(T)

    for cell in cells:
        filename = "Cell{}_{}C_".format(cell, Crate).replace(".", "p") + folder + ".csv"
        imported_data = pd.read_csv(
            os.path.join(root, "data", folder, filename),
            skiprows=skiprows,
        )

        dataset = clean_dataset(imported_data)
        datasets.update({cell: dataset})

    return datasets

def clean_dataset(dataset):
    new_dataset = dataset.dropna(axis=1, how="all")
    replace_dict = {
        "Step Time": "Step Time [s]",
        "Prog Time": "Time [s]",
        "Voltage": "Voltage [V]",
        "Current": "Current [A]",
        "AhAccu": "AhAccu [Ah]",
        "AhPrev": "AhPrev [Ah]",
        "WhAccu": "WhAccu [Wh]",
        "Watt": "Watt [W]",
    }

    if "LogTemp002" in new_dataset.columns:
        T_dict = {"LogTemp001": "Temp Cell [degC]", "LogTemp002": "Temp Ambient [degC]"}
    elif "LogTemp001" in new_dataset.columns:
        if "LogTempPositive" in new_dataset.columns:
            T_dict = {
                "LogTempPositive": "Temp Positive [degC]",
                "LogTempMid": "Temp Cell [degC]",
                "LogTempNegative": "Temp Negative [degC]",
                "LogTemp001": "Temp Ambient [degC]",
            }
        else:
            T_dict = {"LogTemp001": "Temp Cell [degC]"}
    else:
        T_dict = {
            "LogTempPositive": "Temp Positive [degC]",
            "LogTempMid": "Temp Cell [degC]",
            "LogTempNegative": "Temp Negative [degC]",
        }

    replace_dict.update(T_dict)

    new_dataset = new_dataset.rename(columns=replace_dict, errors="raise")

    return new_dataset

