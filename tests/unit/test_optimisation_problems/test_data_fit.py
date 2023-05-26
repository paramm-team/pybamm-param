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
        data = pd.DataFrame()
        parameters_optimise = {
            "Negative electrode diffusivity [m2.s-1]": (5e-15, (2.06e-16, 2.06e-12))
        }
        optimisation_problem = pbparam.DataFit(sim, data, parameters_optimise)

        # Test class variables
        self.assertTrue(optimisation_problem.data.empty)
        self.assertEqual(optimisation_problem.parameters_optimise, parameters_optimise)
        self.assertEqual(optimisation_problem.variables_optimise, ["Voltage [V]"])

        self.assertIsInstance(
            optimisation_problem.parameter_values[
                "Negative electrode diffusivity [m2.s-1]"
            ],
            pybamm.InputParameter,
        )

        self.assertEqual(optimisation_problem.x0, [1.0])
        self.assertEqual(optimisation_problem.bounds, [(0.0412, 412)])

        self.assertEqual(
            optimisation_problem.map_inputs,
            {"Negative electrode diffusivity [m2.s-1]": 0},
        )

        self.assertIsInstance(
            optimisation_problem.simulation.parameter_values[
                "Negative electrode diffusivity [m2.s-1]"
            ],
            pybamm.InputParameter,
        )

        self.assertIsInstance(optimisation_problem.simulation.model, type(model))

        # Test variables_to_optimise
        optimisation_problem = pbparam.DataFit(
            sim,
            data,
            parameters_optimise,
            variables_optimise=["Voltage [V]", "Cell temperature [K]"],
        )
        self.assertEqual(
            optimisation_problem.variables_optimise,
            ["Voltage [V]", "Cell temperature [K]"],
        )

        # Test multiple parameters_optimise with same value
        parameter_names = (
            "Negative electrode diffusivity [m2.s-1]",
            "Positive electrode diffusivity [m2.s-1]",
        )
        parameters_optimise = {parameter_names: (5e-15, (2.06e-16, 2.06e-12))}
        optimisation_problem = pbparam.DataFit(
            sim,
            data,
            parameters_optimise,
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

    def test_setup_objective_function(self):
        model = pybamm.lithium_ion.SPM()
        sim = pybamm.Simulation(model)
        data = pd.DataFrame(
            {
                "Time [s]": [0, 1, 2, 3],
                "Voltage [V]": [3.7, 3.6, 3.5, 3.4],
            }
        )
        parameters_optimise = {
            "Negative electrode diffusivity [m2.s-1]": (5e-15, (2.06e-16, 2.06e-12))
        }
        optimisation_problem = pbparam.DataFit(sim, data, parameters_optimise)

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
        parameters_optimise = {
            "Negative electrode diffusivity [m2.s-1]": (5e-15, (2.06e-16, 2.06e-12))
        }
        optimisation_problem = pbparam.DataFit(sim, data, parameters_optimise)
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
        parameters_optimise = {
            "Negative electrode diffusivity [m2.s-1]": (5e-15, (2.06e-16, 2.06e-12))
        }
        optimisation_problem = pbparam.DataFit(sim, data, parameters_optimise)
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
        parameters_optimise = {
            "Negative electrode diffusivity [m2.s-1]": (5e-15, (2.06e-16, 2.06e-12))
        }
        optimisation_problem = pbparam.DataFit(sim, data, parameters_optimise)

        plot = optimisation_problem._plot(None)

        self.assertIsInstance(plot, pybamm.QuickPlot)
        self.assertListEqual(plot.labels, ["Initial values", "Optimal values"])


if __name__ == "__main__":
    print("Add -v for more debug output")
    import sys

    if "-v" in sys.argv:
        debug = True
    unittest.main()
