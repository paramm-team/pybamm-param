#
# Tests for the Data Fit class
#
import pbparam
import pybamm
import pandas as pd

import unittest


class TestDataFit(unittest.TestCase):
    def test_data_fit_init(self):
        sim = pybamm.Simulation(pybamm.lithium_ion.SPM())
        data = pd.DataFrame()
        parameters_optimise = {
            "Negative electrode diffusivity [m2.s-1]": (5e-15, (2.06e-16, 2.06e-12))
        }
        optimisation_problem = pbparam.DataFit(sim, data, parameters_optimise)
        self.assertTrue(optimisation_problem.data.empty)


if __name__ == "__main__":
    print("Add -v for more debug output")
    import sys

    if "-v" in sys.argv:
        debug = True
    unittest.main()
