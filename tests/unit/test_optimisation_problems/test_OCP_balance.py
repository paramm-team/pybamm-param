#
# Tests for the Data Fit class
#
import pbparam
import pandas as pd

import unittest


class TestOCPBalance(unittest.TestCase):
    def test_init(self):
        optimisation_problem = pbparam.OCPBalance("data_fit", "data_ref")
        self.assertEqual(optimisation_problem.data_fit, ["data_fit"])
        self.assertEqual(optimisation_problem.data_ref, ["data_ref"])

        optimisation_problem = pbparam.OCPBalance(["data_fit"], ["data_ref"])
        self.assertEqual(optimisation_problem.data_fit, ["data_fit"])
        self.assertEqual(optimisation_problem.data_ref, ["data_ref"])

        with self.assertRaisesRegex(ValueError, "The number of fit"):
            optimisation_problem = pbparam.OCPBalance(
                ["data_fit"], ["data_ref1", "data_ref2"]
            )

    def test_setup_objective_function(self):
        data_ref = [
            pd.DataFrame({0: [0.1, 0.3, 0.5, 0.7, 0.9], 1: [5, 4, 3, 2, 1]}),
            pd.DataFrame({0: [0.1, 0.3, 0.5, 0.7, 0.9], 1: [6, 5, 4, 3, 2]}),
        ]

        # Test decreasing fit data
        data_fit = [
            pd.DataFrame({0: [1, 2, 3, 4, 5], 1: [5, 4, 3, 2, 1]}),
            pd.DataFrame({0: [1, 2, 3, 4, 5], 1: [6, 5, 4, 3, 2]}),
        ]
        optimisation_problem = pbparam.OCPBalance(data_fit, data_ref)
        optimisation_problem.setup_objective_function()

        # Check bounds are correct
        self.assertEqual(optimisation_problem.x0, [-0.25, 0.25])
        self.assertEqual(optimisation_problem.bounds, [(-0.275, 1.1), (-0.1, 0.275)])

        # Check cost function is zero at theoretical optimal
        self.assertAlmostEqual(optimisation_problem.objective_function([-0.1, 0.2]), 0)

        # Check extra variables for MLE
        optimisation_problem = pbparam.OCPBalance(
            data_fit, data_ref, cost_function=pbparam.MLE()
        )
        optimisation_problem.setup_objective_function()
        self.assertEqual(optimisation_problem.x0, [-0.25, 0.25, 1, 1])
        self.assertEqual(
            optimisation_problem.bounds,
            [(-0.275, 1.1), (-0.1, 0.275), (1e-16, 1e3), (1e-16, 1e3)],
        )

        # Test increasing fit data
        data_fit = [
            pd.DataFrame({0: [1, 2, 3, 4, 5], 1: [1, 2, 3, 4, 5]}),
            pd.DataFrame({0: [1, 2, 3, 4, 5], 1: [2, 3, 4, 5, 6]}),
        ]

        weights = [2]

        optimisation_problem = pbparam.OCPBalance(data_fit, data_ref, weights)
        optimisation_problem.setup_objective_function()

        # Check bounds are correct
        self.assertEqual(optimisation_problem.x0, [1.25, -0.25])
        self.assertEqual(optimisation_problem.bounds, [(-0.1, 1.375), (-0.275, 0.1)])

        # Check cost function is zero at theoretical optimal
        self.assertAlmostEqual(optimisation_problem.objective_function([1.1, -0.2, 1]), 0)

        # Test data type error
        optimisation_problem = pbparam.OCPBalance(["data_fit"], ["data_ref"])
        with self.assertRaisesRegex(TypeError, "data_ref elements must"):
            optimisation_problem.setup_objective_function()

    def test_plot(self):
        data_ref = [
            pd.DataFrame({0: [0.1, 0.3, 0.5, 0.7, 0.9], 1: [5, 4, 3, 2, 1]}),
            pd.DataFrame({0: [0.1, 0.3, 0.5, 0.7, 0.9], 1: [6, 5, 4, 3, 2]}),
        ]
        data_fit = [
            pd.DataFrame({0: [1, 2, 3, 4, 5], 1: [5, 4, 3, 2, 1]}),
            pd.DataFrame({0: [1, 2, 3, 4, 5], 1: [6, 5, 4, 3, 2]}),
        ]
        optimisation_problem = pbparam.OCPBalance(data_fit, data_ref)

        optimisation_problem.setup_objective_function()

        fig = optimisation_problem._plot([-0.1, 0.2])
        ax = fig.axes[0]

        self.assertEqual(ax.get_xlabel(), "Stoichiometry")
        self.assertEqual(ax.get_ylabel(), "OCP [V]")


if __name__ == "__main__":
    print("Add -v for more debug output")
    import sys

    if "-v" in sys.argv:
        debug = True
    unittest.main()
