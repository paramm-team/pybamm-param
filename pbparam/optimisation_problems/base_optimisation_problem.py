#
# Base optimisation problem class
#

import pybamm
import numpy as np


class BaseOptimisationProblem:
    """
    Base optimisation problem class

    This class provides a base for defining optimization problems and contains
    methods that should be overridden in subclasses to provide specific implementations.
    """

    def __init__(
            self,
            cost_function=None,
            data=None,
            model=None,
            parameters=None,
            variables_to_fit=None
    ):
        """
        Initialize the class properties

        x0 : array-like
            Initial guess for the optimization problem
        bounds : tuple
            bounds of the optimization problem
        scalings : array-like
            scalings for the optimization problem
        cost_function : :class:`pbparam.BaseCostFunction`
            Cost function class to be used in minimisation algorithm.
            The default is Root-Mean Square Error. It can be selected from
            pre-defined built-in functions or defined explicitly
        data : 
            Data object containing the data to be fitted
        model : 
            Model object containing the model to be fitted
        parameters : 
            Parameters object containing the parameters to be fitted
        variables_to_fit : 
            List of variables to be fitted
        """
        # Parameters to be defined in constructor
        self.x0 = None
        self.bounds = None
        self.scalings = None

        # Parameters that can be set by the user
        self.cost_function = cost_function
        assert self.cost_function is not None, "cost_function must be defined"
        self.data = data
        self.model = model
        self.parameters = parameters
        self.variables_to_fit = variables_to_fit

        # This should be a requirement to run if defined, if it's not defined in the
        #  subclass it will pass
        self.setup_objective_function()

    def objective_function(self, x):
        """
        Placeholder method for the objective function

        Subclasses will override this method to provide specific implementations

        Parameters
        ----------
        x : array-like
            independent variable for the objective function

        Returns
        -------
        float
            the value of the objective function
        """
        raise NotImplementedError(
            "objective_function not defined, setup_objective_function needs to"
            " be called first"
        )

    def setup_objective_function(self):
        """
        Placeholder method for setting up the objective function

        Subclasses will override this method to provide specific implementations
        """
        pass

    def calculate_solution(self):
        """
        Placeholder method for calculating the solution of the optimization problem

        Subclasses will override this method to provide specific implementations
        """
        pass

    def update_simulation_parameters(self, simulation):
        """
        Update the simulation object with new parameter values
        """
        # Remove integrator_specs from solver
        solver = simulation.solver
        if hasattr(solver, "integrator_specs"):
            solver.integrator_specs = {}

        # Updating sim params requires recreating the simulation
        new_simulation = pybamm.Simulation(
            simulation.model,
            experiment=getattr(simulation, "experiment", None),
            geometry=simulation.geometry,
            parameter_values=self.parameters,
            submesh_types=simulation.submesh_types,
            var_pts=simulation.var_pts,
            spatial_methods=simulation.spatial_methods,
            solver=solver,
            output_variables=simulation.output_variables,
            C_rate=getattr(simulation, "C_rate", None),
        )

        self.model = new_simulation

    def collect_parameters(self, solve_options=None):
        self.solve_options = solve_options or {}

        # Obtain the new parameters to optimise introduced by the cost function
        self.cost_function_parameters = self.cost_function._get_parameters(
            self.variables_to_fit
        )
        self.joint_parameters = {
            **self.parameters,
            **self.cost_function_parameters,
        }

        # Initialise the parameters_values dictionary
        self.parameter_values = self.model.parameter_values.copy()

        # Initialise the dictionary to map each parameter to optimise to the index of x
        # it corresponds to
        self._process_parameters()

        # Update the simulation parameters to inputs
        for k in self.map_inputs.keys() & self.parameter_values.keys():
            self.parameter_values[k] = "[input]"

    def _process_parameters(self):
        # Assemble the map_inputs dictionary, where the keys are the names parameters to
        # optimise and the values are their index in the x array
        self.map_inputs = {
            key: index
            for index, keys in enumerate(self.joint_parameters)
            for key in (keys if isinstance(keys, tuple) else [keys])
        }

        # Initialise the initial guesses, bounds and scalings for the optimisation
        # TODO: allow these to not be passed at this stage
        self.x0 = np.empty([len(self.joint_parameters)])
        self.bounds = [None] * len(self.joint_parameters)
        self.scalings = np.empty([len(self.joint_parameters)])

        for i, value in enumerate(self.joint_parameters.values()):
            if value[0]:
                scaling = value[0]
            else:
                scaling = 1

            self.scalings[i] = scaling
            self.x0[i] = value[0] / scaling
            self.bounds[i] = tuple(v / scaling for v in value[1])

    def _plot(self, x):
        """
        Placeholder method for plotting the optimization problem

        Subclasses will override this method to provide specific implementations

        Parameters
        ----------
        x : array-like
            independent variable for the plot
        """
        pass
