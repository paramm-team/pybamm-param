#
# Tests for the Data Fit class
#
import pbparam
import pybamm
import pandas as pd
import numpy as np

import unittest


class TestDataFit(unittest.TestCase):
    def test_init(self):
        model = pybamm.lithium_ion.SPM()
        sim = pybamm.Simulation(model)
        data = pd.DataFrame(columns=["Voltage [V]", "Cell temperature [K]"])
        model_parameters = {
            "Negative electrode diffusivity [m2.s-1]": (5e-15, (2.06e-16, 2.06e-12)),
            "Total heat transfer coefficient [W.m-2.K-1]": (0, (0, 1000)),
        }
        optimisation_problem = pbparam.DataFit(sim, data, model_parameters)

        # Test class variables
        self.assertTrue(optimisation_problem.data.empty)
        self.assertEqual(optimisation_problem.model_parameters, model_parameters)
        self.assertEqual(optimisation_problem.variables_optimise, ["Voltage [V]"])

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

        np.testing.assert_array_equal(optimisation_problem.x0, [1.0, 0.0])
        np.testing.assert_array_equal(
            optimisation_problem.bounds, [(0.0412, 412), (0, 1000)]
        )
        np.testing.assert_array_equal(optimisation_problem.scalings, [5e-15, 1.0])

        self.assertEqual(
            optimisation_problem.map_inputs,
            {
                "Negative electrode diffusivity [m2.s-1]": 0,
                "Total heat transfer coefficient [W.m-2.K-1]": 1,
            },
        )

        self.assertIsInstance(
            optimisation_problem.simulation.parameter_values[
                "Negative electrode diffusivity [m2.s-1]"
            ],
            pybamm.InputParameter,
        )
        self.assertIsInstance(
            optimisation_problem.simulation.parameter_values[
                "Total heat transfer coefficient [W.m-2.K-1]"
            ],
            pybamm.InputParameter,
        )

        self.assertIsInstance(optimisation_problem.simulation.model, type(model))

        # Test variables_to_optimise
        optimisation_problem = pbparam.DataFit(
            sim,
            data,
            model_parameters,
            variables_optimise=["Voltage [V]", "Cell temperature [K]"],
        )
        self.assertEqual(
            optimisation_problem.variables_optimise,
            ["Voltage [V]", "Cell temperature [K]"],
        )
        # Test custom_weights
        optimisation_problem = pbparam.DataFit(
            sim,
            data,
            model_parameters,
            variables_optimise=["Voltage [V]", "Cell temperature [K]"],
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
            self.assertIsInstance(
                optimisation_problem.simulation.parameter_values[name],
                pybamm.InputParameter,
            )
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
        with self.assertRaisesRegex(
            ValueError,
            "Length of weights should",
        ):
            pbparam.DataFit(
                sim, data, model_parameters, weights=variable_weights
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

        # Check objective_function raises error before setup
        with self.assertRaisesRegex(
            NotImplementedError, "objective_function not defined"
        ):
            optimisation_problem.objective_function(None)

        # Check objective_function returns a number after setup
        optimisation_problem.setup_objective_function()
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
        self.assertEqual(sol.t[-1], 20)

        # Check inputs are correct
        self.assertEqual(
            sol.all_inputs,
            [{"Negative electrode diffusivity [m2.s-1]": np.array([1e-15])}],
        )

    def test__plot(self):
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

        self.assertIsInstance(plot, pybamm.QuickPlot)
        self.assertListEqual(plot.labels, ["Initial values", "Optimal values"])


if __name__ == "__main__":
    print("Add -v for more debug output")
    import sys

    if "-v" in sys.argv:
        debug = True
    unittest.main()
