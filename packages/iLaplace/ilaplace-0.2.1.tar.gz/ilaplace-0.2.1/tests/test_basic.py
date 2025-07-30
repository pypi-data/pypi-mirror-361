import unittest
from iLaplace import invert_laplace
from mpmath import mp

class TestInvertLaplaceBasic(unittest.TestCase):
    def setUp(self):
        mp.dps = 25

    def test_simple_exponential(self):
        f = lambda s: 1 / (s + 1)
        t = 1.0
        result = invert_laplace(f, t, method="talbot", degree=10)
        expected = mp.exp(-t)
        self.assertAlmostEqual(result, float(expected), places=5)

    def test_invalid_function(self):
        with self.assertRaises(TypeError):
            invert_laplace(123, 1.0)

    def test_invalid_time_type(self):
        f = lambda s: 1 / (s + 1)
        with self.assertRaises(TypeError):
            invert_laplace(f, "not_a_number", method="talbot")

    def test_negative_time(self):
        f = lambda s: 1 / (s + 1)
        with self.assertRaises(ValueError):
            invert_laplace(f, -1.0, method="talbot")

if __name__ == '__main__':
    unittest.main()
