#
# Tests for the RMSE class
#
import pbparam
import numpy as np

import unittest


class TestRMSE(unittest.TestCase):
    def test_init(self):
        cost_function = pbparam.RMSE()
        self.assertEqual(cost_function.name, "Root Mean Square Error")

    def test_evaluate(self):
        cost_function = pbparam.RMSE()
        y_sim = np.ones(4)
        y_data = np.ones(4)
        self.assertEqual(cost_function.evaluate(y_sim, y_data), 0)

        y_sim = np.array([1, 2, 3, 4])
        y_data = np.array([4, 3, 2, 1])
        self.assertAlmostEqual(cost_function.evaluate(y_sim, y_data), 0.89442719)

        y_sim = [np.array([1, 2, 3, 4]), np.array([1, 2, 3])]
        y_data = [np.array([4, 3, 2, 1]), np.array([4, 3, 2])]
        self.assertAlmostEqual(cost_function.evaluate(y_sim, y_data), 1.53271193)

    def test_get_parameters(self):
        cost_function = pbparam.RMSE()
        variables = ["Voltage [V]", "X-averaged temperature [K]"]
        parameters = cost_function._get_parameters(variables)
        expected_result = {}

        self.assertDictEqual(parameters, expected_result)


if __name__ == "__main__":
    print("Add -v for more debug output")
    import sys

    if "-v" in sys.argv:
        debug = True
    unittest.main()
