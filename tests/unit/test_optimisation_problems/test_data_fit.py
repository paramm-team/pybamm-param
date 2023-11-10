#
# Tests for the Data Fit class
#
import pbparam
import pybamm
import pandas as pd
import numpy as np
import unittest

from .test_opt_problem import TestOptimisationProblemTemplate


class TestDataFit(TestOptimisationProblemTemplate):
    def test_init(self):
        model = pybamm.lithium_ion.SPM()
        sim = pybamm.Simulation(model)
        data = pd.DataFrame(columns=["Voltage [V]", "Cell temperature [K]"])
        model_parameters = {
            "Negative electrode diffusivity [m2.s-1]": (5e-15, (2.06e-16, 2.06e-12)),
            "Total heat transfer coefficient [W.m-2.K-1]": (0, (0, 1000)),
        }
        # Numpy will raise a 'RuntimeWarning: Mean of empty slice' on line 205
        # of base_optimisation problem if the data is empty
        with self.assertWarns(RuntimeWarning):
            optimisation_problem = pbparam.DataFit(
                sim,
                data,
                model_parameters
            )
        # Test class variables
        # Check data is empty, as we have provided a datafram with headers
        # but no data and data should not be added
        self.assertTrue(optimisation_problem.data.empty)
        # Check Datafit has initialised with the correct parameters
        self.assertEqual(optimisation_problem.parameters, model_parameters)
        # Check Datafit has initialised with the correct fitting variable
        self.assertEqual(optimisation_problem.variables_to_fit, ["Voltage [V]"])

        # Check that the optimisation problem passed model_parameters has the correct
        # pybamm type
        self.assertIsInstance(
            optimisation_problem.parameter_values[
                "Negative electrode diffusivity [m2.s-1]"
            ],
            pybamm.InputParameter,
        )
        self.assertIsInstance(
            optimisation_problem.parameter_values[
                "Total heat transfer coefficient [W.m-2.K-1]"
            ],
            pybamm.InputParameter,
        )

        # Check the optimisation problem has the correct values, boutnds, and scalings
        np.testing.assert_array_equal(optimisation_problem.x0, [1.0, 0.0])
        np.testing.assert_array_equal(
            optimisation_problem.bounds, [(0.0412, 412), (0, 1000)]
        )
        np.testing.assert_array_equal(optimisation_problem.scalings, [5e-15, 1.0])

        # Check the optimisation problem inputs are correct
        # TODO: Make this comment more descriptive
        self.assertEqual(
            optimisation_problem.map_inputs,
            {
                "Negative electrode diffusivity [m2.s-1]": 0,
                "Total heat transfer coefficient [W.m-2.K-1]": 1,
            },
        )

        # Check the optimisation problem has the correct input parameters
        self.assertIsInstance(
            optimisation_problem.model.parameter_values[
                "Negative electrode diffusivity [m2.s-1]"
            ],
            pybamm.InputParameter,
        )
        self.assertIsInstance(
            optimisation_problem.model.parameter_values[
                "Total heat transfer coefficient [W.m-2.K-1]"
            ],
            pybamm.InputParameter,
        )

        # Check the optimisation problem has the correct model type
        self.assertIsInstance(optimisation_problem.model.model, type(model))

        # Test variables_to_optimise
        optimisation_problem = pbparam.DataFit(
            sim,
            data,
            model_parameters,
            variables_to_fit=["Voltage [V]", "Cell temperature [K]"],
        )
        # Check Datafit has initialised with the correct fitting variable
        self.assertEqual(
            optimisation_problem.variables_to_fit,
            ["Voltage [V]", "Cell temperature [K]"],
        )
        # Test custom_weights
        optimisation_problem = pbparam.DataFit(
            sim,
            data,
            model_parameters,
            variables_to_fit=["Voltage [V]", "Cell temperature [K]"],
            weights={"Voltage [V]": [1], "Cell temperature [K]": [1]},
        )
        # Check Datafit has initialised with the correct weights
        self.assertEqual(
            optimisation_problem.weights,
            {"Voltage [V]": [1], "Cell temperature [K]": [1]},
        )

        # Test multiple model_parameters with same value
        parameter_names = (
            "Negative electrode diffusivity [m2.s-1]",
            "Positive electrode diffusivity [m2.s-1]",
        )
        model_parameters = {parameter_names: (5e-15, (2.06e-16, 2.06e-12))}
        optimisation_problem = pbparam.DataFit(
            sim,
            data,
            model_parameters,
        )
        for name in parameter_names:
            # Check the optimisation problem has the correct input parameters
            self.assertIsInstance(
                optimisation_problem.model.parameter_values[name],
                pybamm.InputParameter,
            )
        # Check the problem has the correct inputs
        # TODO: Make this comment more descriptive
        self.assertEqual(
            optimisation_problem.map_inputs,
            {
                "Negative electrode diffusivity [m2.s-1]": 0,
                "Positive electrode diffusivity [m2.s-1]": 0,
            },
        )

    def test_weights_length_mismatch_data_fit(self):
        model = pybamm.lithium_ion.SPM()
        sim = pybamm.Simulation(model)
        data = pd.DataFrame(
            {
                "Time [s]": [0, 1, 2, 3],
                "Voltage [V]": [3.7, 3.6, 3.5, 3.4],
            }
        )
        model_parameters = {
            "Negative electrode diffusivity [m2.s-1]": (5e-15, (2.06e-16, 2.06e-12))
        }

        variable_weights = {"Voltage [V]": [1, 2]}
        # Check that the length of weights raises an error
        with self.assertRaisesRegex(
            ValueError,
            "Length of weights",
        ):
            pbparam.DataFit(sim, data, model_parameters, weights=variable_weights)

    def test_weights_variables_mismatch_data_fit(self):
        model = pybamm.lithium_ion.SPM()
        sim = pybamm.Simulation(model)
        data = pd.DataFrame(
            {
                "Time [s]": [0, 1, 2, 3],
                "Voltage [V]": [3.7, 3.6, 3.5, 3.4],
            }
        )
        model_parameters = {
            "Negative electrode diffusivity [m2.s-1]": (5e-15, (2.06e-16, 2.06e-12))
        }

        variable_weights = {"Cell temperature [K]": [1]}
        # Check that the weights raises an error
        # TODO: Make this comment more descriptive
        with self.assertRaisesRegex(
            ValueError,
            "Weights dictionary should contain",
        ):
            pbparam.DataFit(sim, data, model_parameters, weights=variable_weights)

    def test_warning_weights_with_MLE(self):
        model = pybamm.lithium_ion.SPM()
        sim = pybamm.Simulation(model)
        data = pd.DataFrame(
            {
                "Time [s]": [0, 1, 2, 3],
                "Voltage [V]": [3.7, 3.6, 3.5, 3.4],
            }
        )
        model_parameters = {
            "Negative electrode diffusivity [m2.s-1]": (5e-15, (2.06e-16, 2.06e-12))
        }

        variable_weights = {"Voltage [V]": [1]}
        cost_function = pbparam.MLE()
        # Check that the class initialises with a warning
        # TODO: Make this comment more descriptive
        with self.assertWarnsRegex(Warning, "MLE calculation"):
            pbparam.DataFit(
                sim,
                data,
                model_parameters,
                cost_function=cost_function,
                weights=variable_weights,
            )

    def test_setup_objective_function(self):
        model = pybamm.lithium_ion.SPM()
        sim = pybamm.Simulation(model)
        data = pd.DataFrame(
            {
                "Time [s]": [0, 1, 2, 3],
                "Voltage [V]": [3.7, 3.6, 3.5, 3.4],
            }
        )
        model_parameters = {
            "Negative electrode diffusivity [m2.s-1]": (5e-15, (2.06e-16, 2.06e-12))
        }
        optimisation_problem = pbparam.DataFit(sim, data, model_parameters)

        # Check objective_function returns a number after setup
        optimisation_problem.setup_objective_function()
        # Check that the objective function does not return None
        self.assertIsNotNone(optimisation_problem.objective_function([1e-15]))

    def test_calculate_solution(self):
        # Test without experiment & initial parameter values
        model = pybamm.lithium_ion.SPM()
        sim = pybamm.Simulation(model)
        data = pd.DataFrame(
            {
                "Time [s]": [0, 1, 2, 3],
                "Voltage [V]": [3.7, 3.6, 3.5, 3.4],
            }
        )
        model_parameters = {
            "Negative electrode diffusivity [m2.s-1]": (5e-15, (2.06e-16, 2.06e-12))
        }
        optimisation_problem = pbparam.DataFit(sim, data, model_parameters)
        sol = optimisation_problem.calculate_solution()

        # Check final time is 3 (from data)
        self.assertEqual(sol.t[-1], 3)

        # Check inputs are correct
        self.assertEqual(
            sol.all_inputs,
            [{"Negative electrode diffusivity [m2.s-1]": np.array([5e-15])}],
        )

        # Test with experiment & passing parameter values
        model = pybamm.lithium_ion.SPM()
        sim = pybamm.Simulation(
            model, experiment=pybamm.Experiment(["Discharge at 1C for 20 seconds"])
        )
        data = pd.DataFrame(
            {
                "Time [s]": [0, 1, 2, 3],
                "Voltage [V]": [3.7, 3.6, 3.5, 3.4],
            }
        )
        model_parameters = {
            "Negative electrode diffusivity [m2.s-1]": (5e-15, (2.06e-16, 2.06e-12))
        }
        optimisation_problem = pbparam.DataFit(sim, data, model_parameters)
        sol = optimisation_problem.calculate_solution([1e-15])

        # Check final time is 3 (from data)
        self.assertEqual(sol.t[-1], 20.)

        # Check inputs are correct
        self.assertEqual(
            sol.all_inputs,
            [{"Negative electrode diffusivity [m2.s-1]": np.array([1e-15])}],
        )

    def test_plot(self):
        model = pybamm.lithium_ion.SPM()
        sim = pybamm.Simulation(model)
        data = pd.DataFrame(
            {
                "Time [s]": [0, 1, 2, 3],
                "Voltage [V]": [3.7, 3.6, 3.5, 3.4],
            }
        )
        model_parameters = {
            "Negative electrode diffusivity [m2.s-1]": (5e-15, (2.06e-16, 2.06e-12))
        }
        optimisation_problem = pbparam.DataFit(sim, data, model_parameters)

        plot = optimisation_problem._plot(None)

        # Check plot is a QuickPlot from pybamm
        self.assertIsInstance(plot, pybamm.QuickPlot)
        # Check plot has the correct labels
        self.assertListEqual(plot.labels, ["Initial values", "Optimal values"])


if __name__ == "__main__":
    print("Add -v for more debug output")
    import sys

    if "-v" in sys.argv:
        debug = True
    unittest.main()
