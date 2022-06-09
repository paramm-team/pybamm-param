import pybamm
import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd
import time
from scipy import optimize
import pyswarms as ps
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
        List of battery cells that will be used.
    param_optimised : list, optional
        List of PyBamm parameters that will be optimized. 
        Default is :
        {"Negative electrode diffusivity [m2.s-1]",
         "Negative electrode reaction coefficient",
         "Total heat transfer coefficient [W.m-2.K-1]",
         "Positive current collector specific heat capacity [J.kg-1.K-1]",
         "Negative current collector specific heat capacity [J.kg-1.K-1]",
         "Negative electrode specific heat capacity [J.kg-1.K-1]",
         "Separator specific heat capacity [J.kg-1.K-1]",
         "Positive electrode specific heat capacity [J.kg-1.K-1]"
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
    param : list or pybamm.ParameterValues, optional
        This is the reference parameter set, which we then update for the adjusted thermal parameters.
        Default is Chen2020 (see PyBaMM documentation for details).
    experiment : pybamm.Experiment class, optional
        Pybamm experiment details. Default is set experiment to be a CC discharge at the defined C-rate followed by a 2-hour relaxation
    """

    def __init__(
        self,
        temperature,
        crate, 
        cell_selected,
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
        param_optimised = {
            "Negative electrode diffusivity [m2.s-1]",
            "Negative electrode reaction coefficient",
            "Total heat transfer coefficient [W.m-2.K-1]",
            "Positive current collector specific heat capacity [J.kg-1.K-1]",
            "Negative current collector specific heat capacity [J.kg-1.K-1]",
            "Negative electrode specific heat capacity [J.kg-1.K-1]",
            "Separator specific heat capacity [J.kg-1.K-1]",
            "Positive electrode specific heat capacity [J.kg-1.K-1]"
        },
        param_compare = pybamm.ParameterValues(chemistry=pybamm.parameter_sets.Chen2020)
            
    ):
        
        self.temperature = temperature
        self.crate = crate
        self.cell_selected = cell_selected
        self.model = model
        self.h = h
        self.cp = cp
        self.param_optimised = param_optimised
        self.param_compare = param_compare
   
        #Import test data 
        dataset = import_thermal_data(crate, temperature)
        data_conc = {"time": [], "voltage": [], "temperature": []}
        
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
        param = pybamm.ParameterValues(chemistry=pybamm.parameter_sets.Chen2020)
        # We now update the parameter set for the adjusted parameters
        param = set_thermal_parameters(param, h, cp, temperature)
        param = set_experiment_parameters(param, crate, temperature)
        param = set_ambient_temperature(param, crate, temperature)
                    
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
       
        
        #Define the optimization function. This function will be minimized by an external algorithm.
    def fitness(self,x):

        #Define the parameters with x[k]
        self.simulation.solve(inputs={"Negative electrode diffusivity [m2.s-1]" : x[0],
                                      "Negative electrode reaction coefficient": x[1],
                                      "Total heat transfer coefficient [W.m-2.K-1]": x[2],
                                      "Positive current collector specific heat capacity [J.kg-1.K-1]": x[3],
                                      "Negative current collector specific heat capacity [J.kg-1.K-1]": x[3],
                                      "Negative electrode specific heat capacity [J.kg-1.K-1]": x[3],
                                      "Separator specific heat capacity [J.kg-1.K-1]": x[3],
                                      "Positive electrode specific heat capacity [J.kg-1.K-1]": x[3]
                                      })
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

    
        # Defining the new PyBamm model with optimized parameters
    def define_model(self, minimum):

        # We now update the parameter set for the adjusted parameters
        param_compare = set_thermal_parameters(self.param_compare, self.h, self.cp, self.temperature)
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
        
        # Solve the model
        
        simulation = pybamm.Simulation(
            self.model,
            parameter_values=self.param,
            experiment=self.experiment,
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
        self.solution = simulation.solution
    def model_plot(self):
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


    
    def optimizer(self, bounds, x0, type='differential_evolution',c1=2.5, c2=0.5, w=0.9, n_particles=50, iters=1000):
        
        self.bounds = bounds
        self.x0 = x0
        self.c1 = c1
        self.c2 = c2
        self.w = w
        self.n_particles = n_particles
        self.iters = iters
        if type=='differential_evolution':
            result = differential_evolution(self.bounds,self.x0)
        elif type=='fmin':
            result = fmin(self.x0)
        elif type=='particle_swarm':
            result = particle_swarm(self.bounds)
        else :
            print("Invalid optimiser type.")
    
def differential_evolution(bounds, x0):
    print("start optimization")
    start = time.process_time()
    print(start)
    result = optimize.differential_evolution(model_build.fitness, bounds, x0=x0)
    end = time.process_time()
    print(end)
    print(end - start)
    print("end optimization")
    return result.x
    def particle_swarm(self, bounds):
        print("start optimization")
        start = time.process_time()
        print(start)
        dimensions = len(self.bounds)
        bounds= np.array(self.bounds)
        min_=[]
        max_=[]
        for i in range(len(bounds)):
            min_.append([bounds[i,0]])
            max_.append([bounds[i,1]])
    
        min_=np.array(min_).T
        max_=np.array(max_).T
        bounds=(min_, max_)
        # Set-up hyperparameters
        options = {'c1': self.c1, 'c2': self.c2, 'w':self.w}
        # Call instance of PSO
        optim = ps.single.GlobalBestPSO(n_particles=self.n_particles, dimensions=dimensions, options=options, bounds=bounds)

        # Perform optimization
        cost, pos = optim.optimize(model.fitness, iters=self.iters)
        end = time.process_time()
        print(end)
        print(end - start)
        print("end optimization")
        return pos
def fmin(x0):
    print("start optimization")
    start = time.process_time()
    print(start)
    result= optimize.fmin(model_build.fitness, x0)
    end = time.process_time()
    print(end)
    print(end - start)
    print("end optimization")
    return result
        
        
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

