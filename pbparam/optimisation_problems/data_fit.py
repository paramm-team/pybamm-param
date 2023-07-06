#
# Data fit class
#

import pbparam
import pybamm


class DataFit(pbparam.BaseOptimisationProblem):
    """
    A class to define an optimisation problem.

    Parameters
    ----------
    simulation : :class:`pybamm.Simulation`
        The simulation to be run to fit to data
    data : :class:`pandas.DataFrame`
         The experimental or reference data to be used in optimisation
         of simulation parameters.
    parameters : dict
        The parameters to be optimised. They should be provided as a dictionary where
        the keys are the names of the variables to be optimised and the values are a
        tuple with the initial guesses and the lower and upper bounds of the
        optimisation. If a key is a list of strings then all the variables in the list
        will take the same value.
    variables_to_fit : str or list of str (optional)
        The variable or variables to optimise in the cost function. The default is
        "Voltage [V]". It can be a string or a list of strings.
    cost_function : :class:`pbparam.BaseCostFunction`
        Cost function class to be used in minimisation algorithm. The default
        is Root-Mean Square Error. It can be selected from pre-defined built-in
        functions or defined explicitly.
    solve_options : dict (optional)
        A dictionary of options to pass to the simulation. The default is None.
    """

    def __init__(
        self,
        simulation,
        data,
        parameters,
        variables_to_fit=["Voltage [V]"],
        cost_function=pbparam.RMSE(),
        solve_options=None,
    ):
        super().__init__(
            model=simulation,
            cost_function=cost_function,
            data=data,
            parameters=parameters,
            variables_to_fit=variables_to_fit
        )

        self.collect_parameters(solve_options)
        self.update_simulation_parameters(simulation)

    def objective_function(self, x):
        """
        Calculate the cost function given the current values of the parameters

        Parameters
        ----------
        x : array-like
            The current values of the parameters

        Returns
        -------
        cost : float
            The calculated cost of the simulation with the current parameters
        """

        # Update the parameter values and solve the simulation using PyBaMM
        input_dict = {
            param: self.scalings[i] * x[i] for param, i in self.map_inputs.items()
        }
        t_end = self.data["Time [s]"].iloc[-1]
        self.solution = self.model.solve([0, t_end], inputs=input_dict)

        # Get the new y values from the simulation
        y_sim = [
            self.solution[v](self.data["Time [s]"])
            for v in self.variables_to_fit
        ]
        y_data = [
            self.data[v]
            for v in self.variables_to_fit
        ]
        sd = [
            x[self.map_inputs[k]]
            for k in self.cost_function_parameters
        ]

        return self.cost_function.evaluate(y_sim, y_data, sd)

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
            # Create a dictionary of inputs using the original parameters
            inputs = {
                param: self.x0[i] * self.scalings[i]
                for param, i in self.map_inputs.items()
            }
        else:
            # Create a dictionary of inputs using the provided parameters
            inputs = {param: parameters[i] for param, i in self.map_inputs.items()}

        # Check if the simulation has an attribute "experiment"
        if getattr(self.model, "experiment", None):
            t_eval = None
        else:
            # Use the final time from the data as t_eval if experiment is not present
            t_eval = [0, self.data["Time [s]"].iloc[-1]]

        # Solve the simulation with the given inputs and t_eval
        solution = self.model.solve(
            t_eval=t_eval, inputs=inputs, **self.solve_options
        )

        return solution

    def _plot(self, x_optimal):
        """
        Plot the optimization result. Should be accessed through the OptimizationResult
        plot method.

        Parameters
        ----------
        x_optimal : array-like
            Optimal values of the parameters found by the optimizer

        Returns
        -------
        plot : pybamm.QuickPlot
            The plot of the optimization result
        """

        # calculate the solution for the initial and optimal parameters
        initial_solution = self.calculate_solution()
        optimal_solution = self.calculate_solution(x_optimal)

        # create a quick plot
        plot = pybamm.QuickPlot(
            [initial_solution, optimal_solution],
            output_variables=self.variables_to_fit,
            labels=["Initial values", "Optimal values"],
        )

        # plot the result
        plot.plot(0)

        # plot the data on the same plot
        for ax, var in zip(plot.axes, self.variables_to_fit):
            data = self.data
            ax.plot(
                data["Time [s]"] / plot.time_scaling_factor,
                data[var],
                "k:",
                label="Data",
            )

        return plot
