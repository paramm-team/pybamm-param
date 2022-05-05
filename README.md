# Pybamm Parameter Optimization Tool
This package is provides parameter optimization for PyBaMM (Python Battery Mathematical Modelling) using different optimization techniques. Currently;
Negative electrode reaction coefficient, Negative electrode diffusivity [m2.s-1], Total heat transfer coefficient [W.m-2.K-1], 
Positive current collector specific heat capacity [J.kg-1.K-1], Negative current collector specific heat capacity [J.kg-1.K-1], 
Negative electrode specific heat capacity [J.kg-1.K-1], Separator specific heat capacity [J.kg-1.K-1],
Positive electrode specific heat capacity [J.kg-1.K-1] are optimized. This can be extended but these 5 parameters has the most significant effect on discharge voltage
and temperature characteristics. 

# Usage of create_model.py
A python function is created for loading files, defining optimization parameters, creating optimization function and plotting comparison graph with Chen2020 values.
After the create_model.py is imported, the model needs to be build as below.
```python3
import create_model
import numpy as np
import os
# Change simulation parameters here
temperature = 25  # in degC, valid values: 0, 10, 25
crate = 1         # valid values: 0.5, 1, 2
cell_selected = ["789"]   # select the cell to optimize
model=create_model.model_build(temperature,crate,cell_selected) # building the PyBaMM model
```
## Defining Initial values and Bounds
Then, Initial values and bounds can be defined for optimization as below.
```python3
# Initial values of parameters
x0 =np.array([5e-14,6.48e-7,20,2.85e3])  

# bounds of the variables as (min,max) {This might need adjustment according to the optimization method.}
bounds = [(2.06e-16,2.06e-12),(2.18589831e-9,2.18589831e-5),(0.1,1000),(2.85, 2.85e6)] 

model.fitness(x0) #initial value of the cost function
```
## Optimization of Parameters
A suitable optimizer can be used to minimize the cost function. SciPy differential_evolution is used below.
```python3
%time # time the solver
from scipy import optimize
minimum = optimize.differential_evolution(model.fitness, bounds, x0=x0)
```
## Plotting the Discharge Cycle of selected cell
In the last step,create_model function has built in plot function to show the discharge cycle for TSPME, Chen2020 and optimized values in 
a same plot for comparison.
```python3
print("Initial cost function value: %s" %model.fitness(x0)) # Initial cost function value

print("Optimized cost function value: %s" %model.fitness(minimum.x)) # Optimized cost function value

print("Optimized parameter values are: %s" %minimum.x) # Print optimized values

model.define_model(minimum.x) # Building the model again with new parameters

model.model_plot() #model_plot funtion to show TSPME, Chen2020 and optimized curves
```
