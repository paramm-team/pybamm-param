#
# Comparison between different number of grid points in mesh
#

import pybamm
from tec_reduced_model.set_parameters import set_thermal_parameters

pybamm.set_logging_level("INFO")


# Define TDFN with a lumped themral model
model = pybamm.lithium_ion.DFN(
    options={
        "thermal": "lumped",
        "dimensionality": 0,
        "cell geometry": "arbitrary",
    },
    name="TDFN",
)

# Change simulation parameters here
temperature = 25  # in degC
Crate = 1

# Define parameter set Chen 2020 (see PyBaMM documentation for details)
# This is the reference parameter set, which is later adjusted for the temperature
param = pybamm.ParameterValues(chemistry=pybamm.parameter_sets.Chen2020)
param = set_thermal_parameters(param, 20, 2.85e6, temperature)

mesh_factors = [1, 2, 4, 8]
solutions = []

var = pybamm.standard_spatial_vars

for factor in mesh_factors:
    var_pts = {
        var.x_n: 20 * factor,
        var.x_s: 20 * factor,
        var.x_p: 20 * factor,
        var.r_n: 30 * factor,
        var.r_p: 30 * factor,
        var.y: 10,
        var.z: 10,
    }
    sim = pybamm.Simulation(
        model,
        parameter_values=param,
        var_pts=var_pts,
        C_rate=Crate,
    )
    sim.model.name
    sim.solve([0, 3600])
    sim.solution.model.name += " x{} mesh".format(factor)
    solutions.append(sim.solution)

pybamm.dynamic_plot(solutions)
