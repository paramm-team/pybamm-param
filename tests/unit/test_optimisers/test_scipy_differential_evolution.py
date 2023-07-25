#
# Tests for the Scipy Differential Evolution Optimiser class
#
import pbparam

import unittest


def parabola(x):
    return x[0] ** 2


class TestScipyDifferentialEvolution(unittest.TestCase):
    def test_scipy_differential_evolution_init(self):
        optimiser = pbparam.ScipyDifferentialEvolution(cost_function=pbparam.MLE())
        self.assertEqual(optimiser.name, "SciPy Differential Evolution optimiser")
        self.assertFalse(optimiser.single_variable)
        self.assertTrue(optimiser.global_optimiser)
        self.assertEqual(optimiser.extra_options, {})


if __name__ == "__main__":
    print("Add -v for more debug output")
    import sys

    if "-v" in sys.argv:
        debug = True
    unittest.main()
