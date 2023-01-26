#
# Tests for the Base Cost Function class
#

import pbparam
import numpy as np
import unittest


class TestMLE(unittest.TestCase):
    def test_init(self):
        cost_function = pbparam.MLE()
        self.assertEqual(cost_function.name, "Maximum Likelihood Estimation")

    def test_evaluate(self):
        cost_function = pbparam.MLE()

        y_sim = np.array([1, 2, 3, 4])
        y_data = y_sim + np.random.normal(0, 0.1, 4)

        self.assertTrue(
            cost_function.evaluate(y_sim, y_data, 0.1)
            < cost_function.evaluate(y_sim, y_data, 1)
        )


if __name__ == "__main__":
    print("Add -v for more debug output")
    import sys

    if "-v" in sys.argv:
        debug = True
    unittest.main()
