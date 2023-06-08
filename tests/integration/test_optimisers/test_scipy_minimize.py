#
# Tests for the Scipy Minimize Optimiser

import pbparam
import unittest
import numpy as np
from tests import sphere, rosenbrock


class TestScipyMinimize(unittest.TestCase):
    def setUp(self):
        self.methods = [
            "Nelder-Mead",
            "Powell",
            "CG",
            "BFGS",
        ]

        self.opt = pbparam.BaseOptimisationProblem()

    def test_sphere(self):
        self.opt.objective_function = sphere
        self.opt.x0 = [2, -2]
        self.opt.bounds = [[-10, 10], [-10, 10]]

        for method in self.methods:
            optimiser = pbparam.ScipyMinimize(method=method)
            result = optimiser.optimise(self.opt)
            np.testing.assert_array_almost_equal(result.x, np.array([0, 0]), decimal=4)

    def test_rosenbrock(self):
        self.opt.objective_function = rosenbrock
        self.opt.x0 = [2, -2, 2, -2]
        self.opt.bounds = [[-10, 10]] * 4

        for method in self.methods:
            optimiser = pbparam.ScipyMinimize(method=method)
            result = optimiser.optimise(self.opt)
            np.testing.assert_array_almost_equal(result.x, np.ones(4), decimal=4)


if __name__ == "__main__":
    print("Add -v for more debug output")
    import sys

    if "-v" in sys.argv:
        debug = True
    unittest.main()
