#
# Tests for the Base Optimisation Problem class
# Code in triple quotes should be used as a guide for writing tests
#

"""
import pbparam
import pybamm
import pandas as pd
import numpy as np
"""

import unittest


class TestOptimisationProblemTemplate(unittest.TestCase):
    # This is a template to build on to make a test for an optimisation problem
    # It is not a test in itself all tests here fail and must be replaced

    def test_init(self):
        # Test that the model is initialised correctly
        """
        # Initilise the class to test
        args = {
            simulation: pybamm.Simulation(pbparam.Model(),),
            data: pd.DataFrame(),
            parameters: {
                "parameter1": 1,
                "parameter2": 2,
            },
            ...
        }
        optimisation_problem = pbparam.OptimisationProblem(args)

        # Test the class properties after initilisation

        # Check the optimisation problem name
        self.assertEqual(optimisation_problem.name, "Template")
        self.assertEqual(optimisation_problem.parameters, args['parameters'])
        for key, value in args["parameters"].items():
            self.assertIsInstance(
                optimisation_problem.parameter_values['key'],
                pybamm.InputParameter)
        """
        unittest.skip("Not implemented")

    def test_setup_objective_function(self):
        # Test that the objective function is set up correctly
        """
        # Initilise the class to test
        args = {
            simulation: pybamm.Simulation(pbparam.Model(),),
            data: pd.DataFrame(),
            parameters: {
                "parameter1": 1,
                "parameter2": 2,
            },
            ...
        }
        optimisation_problem = pbparam.OptimisationProblem(args)
        optimisation_problem.setup_objective_function()

        # Test the objective function is set up correctly

        # Check objective_function returns a number after setup
        self.assertIsNotNone(optimisation_problem.objective_function([1e-15]))
        """
        unittest.skip("Not implemented")

    def test_calculate_solution(self):
        # Test that the solution is calculated correctly for some input
        """
        # Initilise the class to test
        args = {
            simulation: pybamm.Simulation(pbparam.Model(),),
            data: pd.DataFrame(),
            parameters: {
                "parameter1": 1,
                "parameter2": 2,
            },
            ...
        }
        optimisation_problem = pbparam.OptimisationProblem(args)
        solution = optimisation_problem.calculate_solution()

        # Check the solution is calculated correctly
        self.assertEqual(solution, <known_values>)
        """
        unittest.skip("Not implemented")
