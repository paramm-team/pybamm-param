#
# Optimisation problem class
#

import pybamm
import numpy as np
from functools import partial


def update_simulation_parameters(simulation, parameter_values):
    new_simulation = pybamm.Simulation(
        simulation._unprocessed_model,
        experiment=getattr(simulation, "experiment", None),
        geometry=simulation.geometry,
        parameter_values=parameter_values,
        submesh_types=simulation.submesh_types,
        var_pts=simulation.var_pts,
        spatial_methods=simulation.spatial_methods,
        solver=simulation.solver,
        output_variables=simulation.output_variables,
        C_rate=getattr(simulation, "C_rate", None),
    )

    return new_simulation


def cost_function_full(simulation, map_inputs, data, x):
    input_dict = {param: x[i] for param, i in map_inputs.items()}
    t_end = data["Time [s]"].iloc[-1]
    solution = simulation.solve([0, t_end], inputs=input_dict)

    y_sim = solution["Terminal voltage [V]"](data["Time [s]"])
    y_data = data["Terminal voltage [V]"]

    err = y_sim - y_data
    err = err[~np.isnan(err)]

    MSE = np.sum(err**2) / len(err)
    NMSE = MSE / np.mean(y_data)

    return NMSE


class OptimisationProblem(object):
    """A class to define an optimisation problem.

    Parameters
    ----------
    simulation : :class:`pybamm.Simulation`
        The simulation to be run to fit to data
    data : pandas dataframe
        The data to be fit to
    parameters_optimise : dict
        The parameters to be optimised. They should be provided as a dictionary where
        the keys are the names of the variables to be optimised and the values are a
        tuple with the initial guesses and the lower and upper bounds of the
        optimisation. If a key is a list of strings then all the variables in the list
        will take the same value.
        TODO: allow it to be a list of variables and pass the bounds and initial
        guesses when running the optimiser.
    variables_to_optimise : str or list of str (optional)
        The variable or variables to optimise in the cost function. The default is
        "Terminal voltage [V]". It can be a string or a list of strings.
    """

    def __init__(self, simulation, data, parameters_optimise):
        # Allocate init variables
        self.data = data
        self.parameters_optimise = parameters_optimise

        # Keep a copy of the original parameters for convenience and initialise the new
        # parameters
        self.original_parameters = simulation.parameter_values.copy()
        self.parameter_values = simulation.parameter_values.copy()

        # Initialise the dictionary to map each parameter to optimise to the index of x
        # it corresponds to
        self.map_inputs = {}

        # Initialise the initial guesses and bounds for the optimisation
        # TODO: allow these to not be passed at this stage
        self.x0 = np.empty([len(self.parameters_optimise)])
        self.bounds = [None] * len(self.parameters_optimise)

        for i, (param, value) in enumerate(self.parameters_optimise.items()):
            if isinstance(param, str):
                self.parameter_values[param] = "[input]"
                self.map_inputs[param] = i
            elif isinstance(param, (tuple, list)):
                for p in param:
                    self.parameter_values[p] = "[input]"
                    self.map_inputs[p] = i
            else:
                raise TypeError(
                    "parameters_optimise must be a dictionary and its keys should be strings or tuples/lists of strings."
                )

            self.x0[i] = value[0]
            self.bounds[i] = value[1]

        self.simulation = update_simulation_parameters(
            simulation, self.parameter_values
        )

    def define_cost_function(self):
        """ "
        Define the cost function to be minimised

        Parameters
        ----------
        x : array-like
            The values of the parameters to be optimised. Array of real elements of size (n,) where `n` is the number of parameters to be optimised.

        Returns
        -------
        cost : float
            The value of the cost function evaluated at x.
        """
        cost_function = partial(
            cost_function_full, self.simulation, self.map_inputs, self.data
        )
        self.cost_function = cost_function
