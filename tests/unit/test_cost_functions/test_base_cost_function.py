#
# Tests for the Base Cost Function class
#
import pbparam

import unittest


class TestBaseCostFunction(unittest.TestCase):
    def test_init(self):
        cost_function = pbparam.BaseCostFunction()
        self.assertEqual(cost_function.name, "Base Cost Function")

    def test_evaluate(self):
        cost_function = pbparam.BaseCostFunction()
        self.assertIsNone(cost_function.evaluate(None, None, 1))


if __name__ == "__main__":
    print("Add -v for more debug output")
    import sys

    if "-v" in sys.argv:
        debug = True
    unittest.main()
