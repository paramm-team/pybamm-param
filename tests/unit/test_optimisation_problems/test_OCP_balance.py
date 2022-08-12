#
# Tests for the Data Fit class
#
import pbparam
import numpy as np
import pandas as pd

import unittest


class TestOCPBalance(unittest.TestCase):
    def test_OCP_balance_init(self):
        optimisation_problem = pbparam.OCPBalance("data_fit", "data_ref")
        self.assertEqual(optimisation_problem.data_fit, "data_fit")
        self.assertEqual(optimisation_problem.data_ref, "data_ref")

    def test_OCP_balance_data(self):
        data_fit = pd.DataFrame(
            {0: [1, 3, 5, 7, 5, 3, 1], 1: [1, 2, 3, 4, 2.9, 1.9, 0.9]}
        )
        data_ref = (
            pd.DataFrame({0: [0, 1, 2, 3], 1: [1, 2, 3, 4]}),
            pd.DataFrame({0: [3, 2, 1, 0], 1: [4, 2.9, 1.9, 0.9]}),
        )
        optimisation_problem = pbparam.OCPBalance(data_fit, data_ref)

        optimisation_problem.setup_cost_function()

        np.testing.assert_array_equal(
            optimisation_problem.data_fit_ch.to_numpy(),
            np.array([[1, 3, 5, 7], [1, 2, 3, 4]]).transpose(),
        )
        np.testing.assert_array_equal(
            optimisation_problem.data_fit_dch.to_numpy(),
            np.array([[7, 5, 3, 1], [4, 2.9, 1.9, 0.9]]).transpose(),
        )
        np.testing.assert_array_equal(
            optimisation_problem.data_ref_ch([0, 1, 2, 3]), np.array([0.9, 1.9, 2.9, 4])
        )
        np.testing.assert_array_equal(
            optimisation_problem.data_ref_dch([0, 1, 2, 3]), np.array([1, 2, 3, 4])
        )

        self.assertEqual(optimisation_problem.x0, [3.5, -2.0])
        self.assertEqual(optimisation_problem.bounds, [(-35.0, 35.0), (-20.0, 20.0)])


if __name__ == "__main__":
    print("Add -v for more debug output")
    import sys

    if "-v" in sys.argv:
        debug = True
    unittest.main()
