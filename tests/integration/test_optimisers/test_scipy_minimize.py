#
# Tests for the Scipy Minimize Optimiser

import pbparam
import unittest


class TestScipyMinimize(unittest.TestCase):
    def test_parabola(self):
        methods = [
            "Nelder-Mead",
            "Powell",
            "CG",
            "BFGS",
        ]

        opt = pbparam.BaseOptimisationProblem()
        opt.objective_function = lambda x: x[0] ** 2
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
