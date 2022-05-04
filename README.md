# Pybamm Parameter Optimization Tool
This package is provides parameter optimization for PyBaMM (Python Battery Mathematical Modelling) using different optimization techniques. Currently;
Negative electrode reaction coefficient, Negative electrode diffusivity [m2.s-1], Total heat transfer coefficient [W.m-2.K-1], 
Positive current collector specific heat capacity [J.kg-1.K-1], Negative current collector specific heat capacity [J.kg-1.K-1], 
Negative electrode specific heat capacity [J.kg-1.K-1], Separator specific heat capacity [J.kg-1.K-1],
Positive electrode specific heat capacity [J.kg-1.K-1] are optimized. This can be extended but these 5 parameters has the most significant effect on discharge voltage
and temperature characteristics. 

# Usage of create_model.py
A python function is created for loading files, defining optimization parameters, creating optimization function and plotting comparison graph with Chen2020 values.


