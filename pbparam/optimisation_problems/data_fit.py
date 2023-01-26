#
# Data fit class
#

import pbparam
import pybamm
import numpy as np
import copy
from functools import partial


def update_simulation_parameters(simulation, parameter_values):
    # Remove integrator_specs from solver
    solver = simulation.solver
    solver.integrator_specs = {}

    new_simulation = pybamm.Simulation(
        simulation.model,
        experiment=getattr(simulation, "experiment", None),
        geometry=simulation.geometry,
        parameter_values=parameter_values,
        submesh_types=simulation.submesh_types,
        var_pts=simulation.var_pts,
        spatial_methods=simulation.spatial_methods,
        solver=solver,
        output_variables=simulation.output_variables,
        C_rate=getattr(simulation, "C_rate", None),
    )

    return new_simulation


def objective_function_full(opt_problem, x):
    simulation = opt_problem.simulation
    map_inputs = opt_problem.map_inputs
    scalings = opt_problem.scalings
    data = opt_problem.data
    variables_optimise = opt_problem.variables_optimise
    cost_function = opt_problem.cost_function

    input_dict = {param: scalings[i] * x[i] for param, i in map_inputs.items()}
    t_end = data["Time [s]"].iloc[-1]
    solution = simulation.solve([0, t_end], inputs=input_dict)

    y_sim = [solution[v](data["Time [s]"]) for v in variables_optimise]
    y_data = [data[v] for v in variables_optimise]

    return cost_function.evaluate(y_sim, y_data)


class DataFit(pbparam.BaseOptimisationProblem):
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
    variables_optimise : str or list of str (optional)
        The variable or variables to optimise in the cost function. The default is
        "Terminal voltage [V]". It can be a string or a list of strings.
        TODO: implement this
    """

    def __init__(
        self,
        simulation,
        data,
        parameters_optimise,
        variables_optimise=["Terminal voltage [V]"],
        cost_function=pbparam.RMSE(),
    ):

        # Allocate init variables
        self.data = data
        self.parameters_optimise = parameters_optimise
        self.variables_optimise = variables_optimise
        self.cost_function = cost_function

        # Keep a copy of the original parameters for convenience and initialise the new
        # parameters
        self.original_parameters = copy.deepcopy(simulation.parameter_values)
        self.parameter_values = simulation.parameter_values.copy()

        # Initialise the dictionary to map each parameter to optimise to the index of x
        # it corresponds to
        self.map_inputs = {}

        # Initialise the initial guesses, bounds and scalings for the optimisation
        # TODO: allow these to not be passed at this stage
        self.x0 = np.empty([len(self.parameters_optimise)])
        self.bounds = [None] * len(self.parameters_optimise)
        self.scalings = np.empty([len(self.parameters_optimise)])

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
                    "parameters_optimise must be a dictionary and its keys should be "
                    "strings or tuples/lists of strings."
                )

            if value[0]:
                scaling = value[0]

            self.scalings[i] = scaling
            self.x0[i] = value[0] / scaling
            self.bounds[i] = tuple(v / scaling for v in value[1])

        self.simulation = update_simulation_parameters(
            simulation, self.parameter_values
        )

    def setup_objective_function(self):
        """ "
        Define the cost function to be minimised

        Parameters
        ----------
        x : array-like
            The values of the parameters to be optimised. Array of real elements of
            size (n,) where `n` is the number of parameters to be optimised.

        Returns
        -------
        cost : float
            The value of the cost function evaluated at x.
        """
        objective_function = partial(objective_function_full, self)
        self.objective_function = objective_function

    def calculate_solution(self, parameters=None):
        """
        Calculate solution of model.

        Parameters
        ----------
        parameters : array-like (optional)
            Parameters to calcualte the solution for. If not provided, it uses the
            original parameters.

        Returns
        -------
        solution : pybamm.Solution
            The solution for the given inputs.
        """
        if parameters is None:
            inputs = {
                param: self.x0[i] * self.scalings[i]
                for param, i in self.map_inputs.items()
            }
        else:
            inputs = {param: parameters[i] for param, i in self.map_inputs.items()}

        if getattr(self.simulation, "experiment", None):
            t_eval = None
        else:
            t_eval = [0, self.data["Time [s]"].iloc[-1]]

        solution = self.simulation.solve(t_eval=t_eval, inputs=inputs)

        return solution

    def _plot(self, x_optimal):
        """
        Plot the optimisation result. Should be accessed through the OptimisationResult
        plot method.
        """

        initial_solution = self.calculate_solution()
        optimal_solution = self.calculate_solution(x_optimal)

        plot = pybamm.QuickPlot(
            [initial_solution, optimal_solution],
            output_variables=self.variables_optimise,
            labels=["Initial values", "Optimal values"],
        )

        plot.plot(0)

        for ax, var in zip(plot.axes, self.variables_optimise):
            data = self.data
            ax.plot(
                data["Time [s]"] / plot.time_scaling_factor,
                data[var],
                "k:",
                label="Data",
            )

        return plot
