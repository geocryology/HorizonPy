import numpy as np
import unittest

from horizonpy.skyview import svf_helbig_2009, svf_steyn_1980, SVF_discretized, rotate_horizon

from horizonpy.skyview import rotate_horizon


class TestSkyViewHelbig(unittest.TestCase):
    def test_all_sky_obscured(self):
        f = lambda x: x * 0 + 0
        self.assertEqual(svf_helbig_2009(f, 1), 1.0)

    def test_hemisphere_obscured(self):
        f = lambda x: np.array(np.mod(x, 360) < 180, dtype='int32') * 90
        self.assertEqual(svf_helbig_2009(f, 1), 0.5)

    def test_all_sky_open(self):
        f = lambda x: x * 0 + 90
        self.assertEqual(svf_helbig_2009(f, 1), 0.0)

class TestDiscretizedSkyView(unittest.TestCase):
    pass


class TestRotation(unittest.TestCase):

    def rotated_horizons_positive(self):
        rotate_horizon()


if __name__ == '__main__':
    unittest.main(verbosity=2)

