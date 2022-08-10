#
# Tests for the Data Fit class
#
import pbparam
import pybamm
import pandas as pd

import unittest


class TestDataFit(unittest.TestCase):
    def test_data_fit_init(self):
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
        self.assertEqual(
            optimisation_problem.variables_optimise, ["Terminal voltage [V]"]
        )

        self.assertEqual(
            optimisation_problem.original_parameters, model.default_parameter_values
        )
        self.assertIsInstance(
            optimisation_problem.parameter_values[
                "Negative electrode diffusivity [m2.s-1]"
            ],
            pybamm.InputParameter,
        )

        self.assertIsNone(optimisation_problem.initial_solution)
        self.assertIsNone(optimisation_problem.optimised_solution)

        self.assertEqual(optimisation_problem.x0, [5e-15])
        self.assertEqual(optimisation_problem.bounds, [(2.06e-16, 2.06e-12)])

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
            variables_optimise=["Terminal voltage [V]", "Cell temperature [K]"],
        )
        self.assertEqual(
            optimisation_problem.variables_optimise,
            ["Terminal voltage [V]", "Cell temperature [K]"],
        )


if __name__ == "__main__":
    print("Add -v for more debug output")
    import sys

    if "-v" in sys.argv:
        debug = True
    unittest.main()
