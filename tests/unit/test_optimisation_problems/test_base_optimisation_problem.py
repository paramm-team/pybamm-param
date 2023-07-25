#
# Tests for the Base Optimisation Problem class
#
import pbparam

import unittest


class TestBaseOptimisationProblem(unittest.TestCase):
    def test_base_optimisation_problem_init(self):
        optimisation_problem = pbparam.BaseOptimisationProblem(
            cost_function=pbparam.MLE()
        )
        self.assertIsNone(optimisation_problem.x0)
        self.assertIsNone(optimisation_problem.bounds)

    def test_objective_function(self):
        optimisation_problem = pbparam.BaseOptimisationProblem(
            cost_function=pbparam.MLE()
        )
        with self.assertRaisesRegex(
            NotImplementedError, "objective_function not defined"
        ):
            optimisation_problem.objective_function(None)

    def test_setup_objective_function(self):
        optimisation_problem = pbparam.BaseOptimisationProblem(
            cost_function=pbparam.MLE()
        )
        self.assertIsNone(optimisation_problem.setup_objective_function())

    def test_calculate_solution(self):
        optimisation_problem = pbparam.BaseOptimisationProblem(
            cost_function=pbparam.MLE()
        )
        self.assertIsNone(optimisation_problem.calculate_solution())

    def test_plot(self):
        optimisation_problem = pbparam.BaseOptimisationProblem(
            cost_function=pbparam.MLE()
        )
        self.assertIsNone(optimisation_problem._plot(None))


if __name__ == "__main__":
    print("Add -v for more debug output")
    import sys

    if "-v" in sys.argv:
        debug = True
    unittest.main()
