import numpy as np
import unittest

from horizonpy.skyview import sky_view_factor, SVF_discretized


class TestSkyView(unittest.TestCase):
    def test_all_sky_obscured(self):
        f = lambda x: x * 0 + 0
        self.assertEqual(sky_view_factor(f, 1), 1.0)

    def test_hemisphere_obscured(self):
        f = lambda x: np.array(np.mod(x, 360) < 180, dtype='int32') * 90
        self.assertEqual(sky_view_factor(f, 1), 0.5)

    def test_all_sky_open(self):
        f = lambda x: x * 0 + 90
        self.assertEqual(sky_view_factor(f, 1), 0.0)

class TestDiscretizedSkyView(unittest.TestCase):
    pass

if __name__ == '__main__':
    unittest.main(verbosity=2)