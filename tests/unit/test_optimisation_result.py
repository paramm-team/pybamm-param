#
# Tests for the Optimisation Result class
#
import pbparam

import unittest


class TestOptimisationResult(unittest.TestCase):
    def test_optimisation_result_init(self):
        optimisation_result = pbparam.OptimisationResult(
            "x",
            "success",
            "message",
            "fun",
            "raw_result",
            "optimisation_problem",
        )
        self.assertEqual(optimisation_result.x, "x")
        self.assertEqual(optimisation_result.success, "success")
        self.assertEqual(optimisation_result.message, "message")
        self.assertEqual(optimisation_result.fun, "fun")
        self.assertEqual(optimisation_result.raw_result, "raw_result")
        self.assertEqual(
            optimisation_result.optimisation_problem, "optimisation_problem"
        )
        self.assertIsNone(optimisation_result.solve_time)

    def test_str(self):
        optimisation_result = pbparam.OptimisationResult(
            "x",
            "success",
            "message",
            "fun",
            "raw_result",
            "optimisation_problem",
        )

        self.assertEqual(
            optimisation_result.__str__(),
            "\n             Optimal values: x\n        Cost function value: fun"
            "\n                 Solve time: None\n                    Message: message"
            "\n        ",
        )

    def test_plot(self):
        optimisation_result = pbparam.OptimisationResult(
            "x",
            "success",
            "message",
            "fun",
            "raw_result",
            pbparam.BaseOptimisationProblem(),
        )

        plot = optimisation_result.plot(testing=True)
        self.assertIsNone(plot)


if __name__ == "__main__":
    print("Add -v for more debug output")
    import sys

    if "-v" in sys.argv:
        debug = True
    unittest.main()
