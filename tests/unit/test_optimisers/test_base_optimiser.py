#
# Tests for the Base Optimiser class
#
import pbparam
import pybamm

import unittest


class TestBaseOptimiser(unittest.TestCase):
    def test_base_optimiser_init(self):
        optimiser = pbparam.BaseOptimiser()
        self.assertEqual(optimiser.name, "Base optimiser")
        self.assertFalse(optimiser.single_variable)
        self.assertFalse(optimiser.global_optimiser)

    def test_optimise(self):
        optimiser = pbparam.BaseOptimiser()
        optimisation_problem = pbparam.BaseOptimisationProblem()

        _ = optimiser.optimise(optimisation_problem, x0=-1, bounds=-1)

        self.assertEqual(optimiser.x0, -1)
        self.assertEqual(optimiser.bounds, -1)        

    def test_pybamm_logging_level(self):
        optimiser = pbparam.BaseOptimiser()
        optimisation_problem = pbparam.BaseOptimisationProblem()

        # Hack _run_optimiser to test internal logging level
        def hack_optimiser(optimisation_problem, x0, bounds):
            return pybamm.logger.level

        optimiser._run_optimiser = hack_optimiser

        # Test default logging level
        internal_logging_level = optimiser.optimise(optimisation_problem)
        self.assertEqual(pybamm.logger.level, 30)
        self.assertEqual(internal_logging_level, 40)

        # Test custom logging level
        internal_logging_level = optimiser.optimise(
            optimisation_problem, pybamm_logging_level="DEBUG"
        )
        self.assertEqual(pybamm.logger.level, 30)
        self.assertEqual(internal_logging_level, 10)


if __name__ == "__main__":
    print("Add -v for more debug output")
    import sys

    if "-v" in sys.argv:
        debug = True
    unittest.main()
