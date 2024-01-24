#
# Tests for the Data Fit class
#
import pbparam
import pandas as pd

import unittest


class TestOCPBalance(unittest.TestCase):
    def test_init(self):
        data_ref = pd.DataFrame({'Voltage [V]': [0.1, 0.3, 0.5, 0.7, 0.9],
                                 'Time [s]': [5, 4, 3, 2, 1]})
        data_fit = pd.DataFrame({'Voltage [V]': [1, 2, 3, 4, 5],
                                 'Time [s]': [5, 4, 3, 2, 1]})

        optimisation_problem = pbparam.OCPBalance(data_fit=data_fit, data_ref=data_ref)
        self.assertEqual(optimisation_problem.data, [data_fit])
        self.assertEqual(optimisation_problem.model, [data_ref])

        optimisation_problem = pbparam.OCPBalance(
            data_fit=[data_fit],
            data_ref=[data_ref]
        )
        self.assertEqual(optimisation_problem.data, [data_fit])
        self.assertEqual(optimisation_problem.model, [data_ref])

        with self.assertRaisesRegex(ValueError, "The number of fit"):
            optimisation_problem = pbparam.OCPBalance(
                ["data_fit"], ["data_ref1", "data_ref2"]
            )

    def test_setup_objective_function(self):
        data_ref = [
            pd.DataFrame({'Voltage [V]': [0.1, 0.3, 0.5, 0.7, 0.9],
                          'Time [s]': [5, 4, 3, 2, 1]}),
            pd.DataFrame({'Voltage [V]': [0.1, 0.3, 0.5, 0.7, 0.9],
                          'Time [s]': [6, 5, 4, 3, 2]}),
        ]

        # Test decreasing fit data
        data_fit = [
            pd.DataFrame({'Voltage [V]': [1, 2, 3, 4, 5],
                          'Time [s]': [5, 4, 3, 2, 1]}),
            pd.DataFrame({'Voltage [V]': [1, 2, 3, 4, 5],
                          'Time [s]': [6, 5, 4, 3, 2]}),
        ]
        optimisation_problem = pbparam.OCPBalance(data_fit, data_ref)

        # Check bounds are correct
        self.assertEqual(optimisation_problem.x0, [-0.25, 0.25])
        self.assertEqual(optimisation_problem.bounds, [(-100000, 100000),
                                                       (-100000, 100000)])

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
            [(-100000, 100000), (-100000, 100000),
             (-100000, 100000), (-100000, 100000)],
        )

        # Test increasing fit data
        data_fit = [
            pd.DataFrame({'Voltage [V]': [1, 2, 3, 4, 5], 'Time [s]': [1, 2, 3, 4, 5]}),
            pd.DataFrame({'Voltage [V]': [1, 2, 3, 4, 5], 'Time [s]': [2, 3, 4, 5, 6]}),
        ]

        optimisation_problem = pbparam.OCPBalance(data_fit, data_ref)
        optimisation_problem.setup_objective_function()

        # Check bounds are correct
        self.assertEqual(optimisation_problem.x0, [1.25, -0.25])
        self.assertEqual(optimisation_problem.bounds, [(-100000, 100000),
                                                       (-100000, 100000)])

        # Check cost function is zero at theoretical optimal
        self.assertAlmostEqual(optimisation_problem.objective_function([1.1, -0.2]), 0)

        # Test data type error
        with self.assertRaisesRegex(TypeError,
                                    "data elements must be all array-like objects"):
            optimisation_problem = pbparam.OCPBalance(["data_fit"], ["data_ref"])

    def test_weights_length_mismatch(self):
        data_fit = [
            pd.DataFrame({'Voltage [V]': [1, 2, 3, 4, 5],
                          'Time [s]': [5, 4, 3, 2, 1]}),
            pd.DataFrame({'Voltage [V]': [1, 2, 3, 4, 5],
                          'Time [s]': [6, 5, 4, 3, 2]}),
        ]
        data_ref = [
            pd.DataFrame({'Voltage [V]': [0.1, 0.3, 0.5, 0.7, 0.9],
                          'Time [s]': [5, 4, 3, 2, 1]}),
            pd.DataFrame({'Voltage [V]': [0.1, 0.3, 0.5, 0.7, 0.9],
                          'Time [s]': [6, 5, 4, 3, 2]}),
        ]
        weights = [1, 2, 3, 4]  # Mismatched weights length

        with self.assertRaisesRegex(
            ValueError, "Weights should have the same length as data_ref."
        ):
            pbparam.OCPBalance(data_fit, data_ref, weights=weights)

    def test_warning_weights_with_MLE(self):
        data_fit = [
            pd.DataFrame({'Voltage [V]': [1, 2, 3, 4, 5],
                          'Time [s]': [5, 4, 3, 2, 1]}),
            pd.DataFrame({'Voltage [V]': [1, 2, 3, 4, 5],
                          'Time [s]': [6, 5, 4, 3, 2]}),
        ]
        data_ref = [
            pd.DataFrame({'Voltage [V]': [0.1, 0.3, 0.5, 0.7, 0.9],
                          'Time [s]': [5, 4, 3, 2, 1]}),
            pd.DataFrame({'Voltage [V]': [0.1, 0.3, 0.5, 0.7, 0.9],
                          'Time [s]': [6, 5, 4, 3, 2]}),
        ]
        weights = {'Voltage [V]': [1, 1, 1, 1, 1], 'Time [s]': [1, 1, 1, 1, 1]}
        cost_function = pbparam.MLE()
        with self.assertWarnsRegex(Warning, "MLE calculation"):
            pbparam.OCPBalance(
                data_fit, data_ref, cost_function=cost_function, weights=weights
            )

    def test_plot(self):
        data_ref = [
            pd.DataFrame({'Voltage [V]': [0.1, 0.3, 0.5, 0.7, 0.9],
                          'Time [s]': [5, 4, 3, 2, 1]}),
            pd.DataFrame({'Voltage [V]': [0.1, 0.3, 0.5, 0.7, 0.9],
                          'Time [s]': [6, 5, 4, 3, 2]}),
        ]
        data_fit = [
            pd.DataFrame({'Voltage [V]': [1, 2, 3, 4, 5],
                          'Time [s]': [5, 4, 3, 2, 1]}),
            pd.DataFrame({'Voltage [V]': [1, 2, 3, 4, 5],
                          'Time [s]': [6, 5, 4, 3, 2]}),
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
