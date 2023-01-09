#
# Tests for the Base Cost Function class
#
import pbparam

import unittest


class TestMLE(unittest.TestCase):
    def test_init(self):
        cost_function = pbparam.MLE()
        self.assertEqual(cost_function.name, "Maximum Likelihood Estimation")

    def test_evaluate(self):
        cost_function = pbparam.MLE()
        self.assertIsNone(cost_function.evaluate(None, None, None))


if __name__ == "__main__":
    print("Add -v for more debug output")
    import sys

    if "-v" in sys.argv:
        debug = True
    unittest.main()
