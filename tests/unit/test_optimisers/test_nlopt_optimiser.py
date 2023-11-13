#
# Tests for the Scipy Differential Evolution Optimiser class
#
import pbparam
import unittest


class TestProblem(pbparam.BaseOptimisationProblem):
    def __init__():
        super().__init__()

    def parabola(x):
        return x[0] ** 2


class TestNlopt(unittest.TestCase):
    def test_nlopt_init(self):
        optimiser = pbparam.Nlopt('LN_BOBYQA', ['x'])
        self.assertEqual(optimiser.name, "Nlopt optimiser with LN_BOBYQA method")
        self.assertFalse(optimiser.single_variable)
        self.assertFalse(optimiser.global_optimiser)
        opt_problem = TestProblem()
        optimiser.optimise(parabola, [1])


if __name__ == "__main__":
    print("Add -v for more debug output")
    import sys

    if "-v" in sys.argv:
        debug = True
    unittest.main()
