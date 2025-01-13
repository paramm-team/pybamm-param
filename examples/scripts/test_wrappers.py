import unittest
from mle import mle_example
from multiple_variable_fit import mvf_example
from ocp_balance import ocp_example
from scipy_differential_evolution import scipy_diff_example
from scipy_minimize import scipy_min_example


# Make the example discoverable by the test runner
class TestMLEExample(unittest.TestCase):
    def test_mle_example(self):
        mle_example(suppress_plot=True)


# Make the example discoverable by the test runner
class TestMultipleVariableFit(unittest.TestCase):
    def test_mvf_example(self):
        mvf_example(suppress_plot=True)


# Make the example discoverable by the test runner
class TestOCPBalance(unittest.TestCase):
    def test_ocp_example(self):
        ocp_example(suppress_plot=True)


class TestScipyDiffEvolution(unittest.TestCase):
    def test_scipy_diff_example(self):
        scipy_diff_example(suppress_plot=True)


class TestScipyMinimize(unittest.TestCase):
    def test_scipy_min_example(self):
        scipy_min_example(suppress_plot=True)


if __name__ == "__main__":
    print("Add -v for more debug output")
    import sys

    if "-v" in sys.argv:
        debug = True
    unittest.main()
