#
# Data fit class
#

import pbparam
import pybamm


class GITT(pbparam.BaseOptimisationProblem):
    """
    A class to define an optimisation problem.

    Parameters
    ----------
    simulation : :class:`pybamm.Simulation`
        The simulation to be run to fit to data
    data : :class:`pandas.DataFrame`
         The experimental or reference data to be used in optimisation
         of simulation parameters.
    cost_function : :class:`pbparam.BaseCostFunction`
        Cost function class to be used in minimisation algorithm. The default
        is Root-Mean Square Error. It can be selected from pre-defined built-in
        functions or defined explicitly.
    solve_options : dict (optional)
        A dictionary of options to pass to the simulation. The default is None.
    """

    def __init__(
        self,
        param_dict,
        gitt_model,
        data,
        cost_function=pbparam.RMSE(),
        solve_options=None,
    ):
        param = pybamm.ParameterValues(param_dict)
        simulation = pybamm.Simulation(gitt_model, parameter_values=param)
        super().__init__(
            model=simulation,
            cost_function=cost_function,
            data=data,
            parameters={
                "Positive electrode diffusivity [m2.s-1]": (
                    5e-14,
                    (2.06e-16, 2.06e-12),
                ),
                "Reference OCP [V]": (4.2, (0, 5)),
            },
            variables_to_fit=["Voltage [V]"],
        )

        self.collect_parameters(solve_options)
        self.update_simulation_parameters(simulation)

    def objective_function(self, x):
        # create a dict of input values from the current parameters
        input_dict = {
            param: self.scalings[i] * x[i] for param, i in self.map_inputs.items()
        }
        t_end = self.data["Time [s]"].iloc[-1]
        solution = self.model.solve([0, t_end], inputs=input_dict)

        y_sim = [solution[v](self.data["Time [s]"]) for v in self.variables_to_fit]
        y_data = [self.data[v] for v in self.variables_to_fit]
        sd = [x[self.map_inputs[k]] for k in self.cost_function_parameters]

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
        solution = self.model.solve(t_eval=t_eval, inputs=inputs, **self.solve_options)

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
        #
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
