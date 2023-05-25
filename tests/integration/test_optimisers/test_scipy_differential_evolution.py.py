#
# Tests for the Scipy Minimize Optimiser

import pbparam
import unittest
from tests import parabola


class TestScipyDifferentialEvolution(unittest.TestCase):
    def test_parabola(self):
        opt = pbparam.BaseOptimisationProblem()
        opt.objective_function = parabola
        opt.x0 = 2
        opt.bounds = [[-10, 10]]

        optimiser = pbparam.ScipyDifferentialEvolution()
        result = optimiser.optimise(opt)
        self.assertAlmostEqual(result.x[0], 0, places=4)

    def test_parabola_multiple_workers(self):
        opt = pbparam.BaseOptimisationProblem()
        opt.objective_function = parabola
        opt.x0 = 2
        opt.bounds = [[-10, 10]]

        optimiser = pbparam.ScipyDifferentialEvolution(
            extra_options={"workers": 2, "polish": True, "updating": "deferred"}
        )
        result = optimiser.optimise(opt)
        self.assertAlmostEqual(result.x[0], 0, places=4)


if __name__ == "__main__":
    print("Add -v for more debug output")
    import sys

    if "-v" in sys.argv:
        debug = True
    unittest.main()
