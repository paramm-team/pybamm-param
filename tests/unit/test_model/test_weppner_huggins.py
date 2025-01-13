#
# Tests for the Basic GITT model
#
import pbparam
import pybamm

import unittest


class TestWeppnerHuggins(unittest.TestCase):
    def test_init(self):
        model = pbparam.WeppnerHuggins()
        self.assertEqual(model.name, "WeppnerHuggins model")

    def test_simulation(self):
        model = pbparam.WeppnerHuggins()
        param = model.default_parameter_values
        param.update(
            {
                "Reference OCP [V]": 4.2,
                "Derivative of the OCP wrt stoichiometry [V]": -1,
                "Effective resistance [Ohm]": 0.1,
                "Positive particle diffusivity [m2.s-1]": 4e-15
            },
            check_already_exists=False,
        )
        simulation = pybamm.Simulation(model, parameter_values=param)
        solution = simulation.solve([0, 100])
        self.assertEqual(len(solution["Voltage [V]"].entries), 100)
        self.assertAlmostEqual(solution["Voltage [V]"].entries[-1], 4.1422354008232976)


if __name__ == "__main__":
    print("Add -v for more debug output")
    import sys

    if "-v" in sys.argv:
        debug = True
    unittest.main()
