#
# Tests for the Base Optimisation Problem class
#
import pbparam

import unittest


class TestBaseOptimisationProblem(unittest.TestCase):
    def test_base_optimisation_problem_init(self):
        optimisation_problem = pbparam.BaseOptimisationProblem()
        self.assertIsNone(optimisation_problem.x0)
        self.assertIsNone(optimisation_problem.bounds)

    def test_cost_function(self):
        optimisation_problem = pbparam.BaseOptimisationProblem()
        self.assertTrue(hasattr(optimisation_problem, "cost_function"))

    def test_setup_cost_function(self):
        optimisation_problem = pbparam.BaseOptimisationProblem()
        self.assertTrue(hasattr(optimisation_problem, "setup_cost_function"))


if __name__ == "__main__":
    print("Add -v for more debug output")
    import sys

    if "-v" in sys.argv:
        debug = True
    unittest.main()
