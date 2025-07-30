import unittest
from mpmath import mp
from iLaplace import invert_laplace

class TestInverseLaplace(unittest.TestCase):

    def test_exp_function(self):
        mp.dps = 15
        f = lambda s: 1 / (s + 2)
        val = invert_laplace(f, 1.0)
        expected = mp.exp(-2)
        self.assertAlmostEqual(float(val), float(expected), places=5)

    def test_zero_time(self):
        f = lambda s: 1 / (s + 1)
        val = invert_laplace(f, 0.0)
        self.assertTrue(isinstance(val, (int, float, complex)))

if __name__ == '__main__':
    unittest.main()