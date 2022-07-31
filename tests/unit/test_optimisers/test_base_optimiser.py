#
# Tests for the Base Optimiser class
#
import pbparam

import unittest


class TestBaseOptimiser(unittest.TestCase):
    def test_base_optimiser_init(self):
        optimiser = pbparam.BaseOptimiser()
        self.assertEqual(optimiser.name, "Base optimiser")
        self.assertFalse(optimiser.single_variable)
        self.assertFalse(optimiser.global_optimiser)


if __name__ == "__main__":
    print("Add -v for more debug output")
    import sys

    if "-v" in sys.argv:
        debug = True
    unittest.main()
