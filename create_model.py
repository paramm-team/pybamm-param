import pybamm
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import time
import os
from scipy import optimize
from pyswarms.utils.functions import single_obj as fx
from tec_reduced_model.set_parameters import (
    set_thermal_parameters,
    set_experiment_parameters,
    set_ambient_temperature,
)
plt.style.use(['science','vibrant'])

plt.rcParams.update({
    "font.family": "sans-serif",
    "text.usetex": False,
    "font.size": 8,
    "axes.labelsize": 10,
})

#build class first for PyBamm model
class model_build(object):  
        
    """Build the PyBamm model.
    Parameters
    ----------
    temperature : float
        Temperature value of the experiment.
    crate : float
        Crate value of the experiment data.
    cell_selected : list
        List of battery cell that will be used.
    param_optimised : dict
        Dictionary of PyBamm parameters that will be optimized with their inital values and bounds. 
        For example :
                {"Negative electrode diffusivity [m2.s-1]":(5e-14,(2.06e-16,2.06e-12)),
                 "Negative electrode reaction coefficient":(6.48e-7,(2.18589831e-9,2.18589831e-5)),
                 "Total heat transfer coefficient [W.m-2.K-1]":(20,(0.1,1000)),
                 ("Positive current collector specific heat capacity [J.kg-1.K-1]",
                  "Negative current collector specific heat capacity [J.kg-1.K-1]",
                  "Negative electrode specific heat capacity [J.kg-1.K-1]",
                  "Separator specific heat capacity [J.kg-1.K-1]",
                  "Positive electrode specific heat capacity [J.kg-1.K-1]"):(2.85e3,(2.85, 2.85e6))
                 }
    model : Pybamm model, optional
        Pybamm model to be used.
        Default is :
        pybamm.lithium_ion.SPMe(
            options={
                "thermal": "lumped",
                "dimensionality": 0,
                "cell geometry": "arbitrary",
                "electrolyte conductivity": "integrated",
             },
             name="TSPMe",
        )
    h : float, optional
        h value to calculate h_factor in thermal parameters. Default is 16.
    cp : float, optional
        cp value to calculate cp_factor in thermal parameters. Default is 2.32e6.
    param_default : list or pybamm.ParameterValues, optional
        This is the default reference parameter set, which we then update for the adjusted thermal parameters.
        Default is Chen2020 (see PyBaMM documentation for details).
    experiment : pybamm.Experiment class, optional
        Pybamm experiment details. Default is set experiment to be a CC discharge at the defined C-rate followed by a 2-hour relaxation
    """

    def __init__(
        self,
        temperature,
        crate, 
        cell_selected,
        param_optimised,
        model = pybamm.lithium_ion.SPMe(
            options={
                "thermal": "lumped",
                "dimensionality": 0,
                "cell geometry": "arbitrary",
                "electrolyte conductivity": "integrated",
            },
            name="TSPMe",
        ),
        h = 16,
        cp = 2.32e6,
        param_default = pybamm.ParameterValues(chemistry=pybamm.parameter_sets.Chen2020)
            
    ):
        
        self.temperature = temperature
        self.crate = crate
        self.cell_selected = cell_selected
        self.model = model
        self.h = h
        self.cp = cp
        self.param_optimised = param_optimised
        #self.param_default = param_default
        
        pybamm.set_logging_level("ERROR") #Supress the errors from PyBamm
   
        #Import test data 
        dataset = import_thermal_data(crate, temperature)
        data_conc = {"time": [], "voltage": [], "temperature": []}
        
        prm_updt={}
        x0=np.empty([len(param_optimised)])
        bounds=[None]*len(param_optimised)
        for index,item in enumerate(param_optimised):
            if type(item)==str:
                prm_updt[item]="[input]"
                #prm_func[item]='x[%s]'%index
                x0[index]=param_optimised[item][0]
                bounds[index]=param_optimised[item][1]
            elif type(item)==tuple:
                i=0
                for i in range(len(item)):
                    prm_updt[item[i]]="[input]"
                    #prm_func[item[i]]='x[%s]'%index
                x0[index]=param_optimised[item][0]
                bounds[index]=param_optimised[item][1]
            else:
                print('data type is not supported')
        #self.prm_func=prm_func
        self.x0 = x0
        self.bounds = bounds
        
        #store real-world test data in data_conc with time, temperature and voltage
        for cell, data in dataset.items():
            if cell in cell_selected:
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
        
        # We now update the parameter set for the adjusted parameters
        param = set_thermal_parameters(param_default, h, cp, temperature)
        param = set_experiment_parameters(param, crate, temperature)
        param = set_ambient_temperature(param, crate, temperature)
                    
        #Define the parameters to be optimized
        param.update(prm_updt, check_already_exists=False)
            
        self.param = param
            
        self.experiment = pybamm.Experiment(
            [
                "Discharge at {}C until 2.5 V (5 seconds period)".format(crate),
                "Rest for 2 hours",
            ],period="30 seconds")
        # Solve the model
        self.simulation = pybamm.Simulation(
            model,
            parameter_values=param,
            experiment=self.experiment,
            )
        self.data_conc = data_conc
        
    def get_values(self):    
        return self.x0, self.bounds
       
        
        #Define the optimization function. This function will be minimized by an external algorithm.
    def fitness(self, x):
    
        #Define the parameters with x[k]
        #x=np.empty([len(self.x0)])
        #print({k:v for k, v in self.prm_func.items()})
        #self.simulation.solve(inputs={k:exec(v) for k, v in self.prm_func.items()})
        prm_func={}
        for index,item in enumerate(self.param_optimised):
            if type(item)==str:
                prm_func[item]=x[index]
            elif type(item)==tuple:
                i=0 
                for i in range(len(item)):
                    prm_func[item[i]]=x[index]
        self.simulation.solve(inputs=prm_func)
        solution = self.simulation.solution
        
        """ Temperature and voltage cost functions defined here. R_squared function in the auxiliary functions is used.
            Then they are normalized to get equal effect on the cost function. Sum of normalized functions returned. 
            This sum could be minimized."""
        
        temp_r_squared=1-R_squared(solution["X-averaged cell temperature [K]"],
                                   self.data_conc["time"], (self.data_conc["temperature"] + 273.15))
        volt_r_squared=1-R_squared(solution["Terminal voltage [V]"], self.data_conc["time"], self.data_conc["voltage"])
        temp_normalized=temp_r_squared/(np.average(self.data_conc["temperature"]+273.15))
        volt_normalized=volt_r_squared/(np.average(self.data_conc["voltage"]))
                      
        return np.array(temp_normalized+volt_normalized)

    def optimiser(self, method='differential_evolution'):
        if method=='differential_evolution':
            result = self.differential_evolution()
            self.result=result
        elif method=='fmin':
            result = self.fmin()
            self.result=result
    
    def differential_evolution(self, workers=-1):
        print("start optimization")
        start = time.process_time()
        print(start)
        result = optimize.differential_evolution(self.fitness, self.bounds, x0=self.x0, workers=workers)
        end = time.process_time()
        print(end)
        print(end - start)
        print("end optimization")
        return result.x
    
    def fmin(self):
        print("start optimization")
        start = time.process_time()
        print(start)
        result= optimize.fmin(self.fitness, x0= self.x0)
        end = time.process_time()
        print(end)
        print(end - start)
        print("end optimization")
        return result
    
        # Defining the new PyBamm model with optimized parameters
    def model_plot(self, param_compare=pybamm.ParameterValues(chemistry=pybamm.parameter_sets.Chen2020)):
        
        
        # We now update the parameter set for the adjusted parameters
        param_compare = set_thermal_parameters(param_compare, self.h, self.cp, self.temperature)
        param_compare = set_experiment_parameters(param_compare, self.crate, self.temperature)
        param_compare = set_ambient_temperature(param_compare, self.crate, self.temperature)

        # Solve the model
        simulation_compare = pybamm.Simulation(
            self.model,
            parameter_values=param_compare,
            experiment=self.experiment,
        )
        simulation_compare.solve()
        self.solution_compare = simulation_compare.solution
        
        prm_min={}
        for index,item in enumerate(self.param_optimised):
            if type(item)==str:
                prm_min[item]=self.result[index]
            elif type(item)==tuple:
                i=0 
                for i in range(len(item)):
                    prm_min[item[i]]=self.result[index]
        
        # Solve the model
        
        simulation = pybamm.Simulation(
            self.model,
            parameter_values=self.param,
            experiment=self.experiment,
        )
        simulation.solve(inputs=prm_min)
        self.solution = simulation.solution
        
    
        fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
        dataset = import_thermal_data(self.crate, self.temperature)
        data_conc = {"time": [], "voltage": [], "temperature": []}
    
        for cell, data in dataset.items():
            if cell in self.cell_selected:
                idx_start, idx_end = get_idxs(data, self.crate * 5, 5 / 3)
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
                    self.solution["Time [s]"].entries,
                    self.solution["Terminal voltage [V]"].entries,
                    color="black",
                    label="TSPMe",
                )
                
                axes[0].plot(
                    self.solution_compare["Time [s]"].entries,
                    self.solution_compare["Terminal voltage [V]"].entries,
                    'r--',
                    label="Initial Model",
                )
    
                axes[0].scatter(
                    0,
                    self.solution["X-averaged battery open circuit voltage [V]"].entries[0],
                    marker="x",
                    color="black"
                )
                axes[0].scatter(
                    0,
                    self.solution_compare["X-averaged battery open circuit voltage [V]"].entries[0]
                )
    
                axes[0].set_xlabel("Time (s)")
                axes[0].set_ylabel("Voltage (V)")
        
                axes[1].plot(
                    self.solution["Time [s]"].entries,
                    self.solution["X-averaged cell temperature [K]"].entries - 273.15,
                    color="black",
                    label="TSPMe",
                )
                axes[1].plot(
                    self.solution_compare["Time [s]"].entries,
                    self.solution_compare["X-averaged cell temperature [K]"].entries - 273.15,
                    'r--',
                    label="Initial Model",
                )
        
                axes[1].set_xlabel("Time (s)")
                axes[1].set_ylabel("Cell temperature (°C)")
                axes[1].legend()
                fig.suptitle("Ambient temperature: {} °C, C-rate: {}C".format(self.temperature, self.crate))
        
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
