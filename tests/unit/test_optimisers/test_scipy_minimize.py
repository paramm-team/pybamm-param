#
# Tests for the Scipy Minimize Optimiser class
#
import pbparam

import unittest


class TestScipyMinimize(unittest.TestCase):
    def test_scipy_minimize_init(self):
        optimiser = pbparam.ScipyMinimize(method="method")
        self.assertEqual(optimiser.name, "SciPy Minimize optimiser with method method")
        self.assertEqual(optimiser.method, "method")
        self.assertFalse(optimiser.single_variable)
        self.assertFalse(optimiser.global_optimiser)
        self.assertEqual(optimiser.extra_options, {})

if __name__ == "__main__":
    print("Add -v for more debug output")
    import sys

    if "-v" in sys.argv:
        debug = True
    unittest.main()
