#
# Tests for the Scipy Minimize Optimiser class
#
import pbparam

import unittest

from tests.shared import DummyOptimisationProblem


class TestScipyMinimize(unittest.TestCase):
    def test_scipy_minimize_init(self):
        optimiser = pbparam.ScipyMinimize(method="method")
        self.assertEqual(optimiser.name, "SciPy Minimize optimiser with method method")
        self.assertEqual(optimiser.method, "method")
        self.assertFalse(optimiser.single_variable)
        self.assertFalse(optimiser.global_optimiser)
        self.assertEqual(optimiser.extra_options, {})

    def test_optimiser(self):
        methods = [
            "Nelder-Mead",
            "Powell",
            "CG",
            "BFGS",
        ]

        opt = DummyOptimisationProblem()
        opt.cost_function = lambda x: x[0] ** 2
        opt.x0 = 2
        opt.bounds = [[-10, 10]]

        for method in methods:
            optimiser = pbparam.ScipyMinimize(method=method)
            result = optimiser.optimise(opt)
            self.assertAlmostEqual(result.x[0], 0, places=6)


if __name__ == "__main__":
    print("Add -v for more debug output")
    import sys

    if "-v" in sys.argv:
        debug = True
    unittest.main()
