from abc import ABC, abstractmethod
import numpy as np


class Lens(ABC):

    @staticmethod
    @abstractmethod
    def horizon_from_radius(dot_radius, grid_radius):
        pass

    @staticmethod
    @abstractmethod
    def radius_from_horizon(horizon, grid_radius):
        pass

class SunexLens(Lens):
    """# From Empey (2015)"""

    NAME = "Sunex Lens"
    INFO = """Calibration of 5.6 mm Sunex lens by Empey (2015)"""


    @staticmethod
    def horizon_from_radius(dot_radius, grid_radius):

        # Enter total field of view of Sunex camera (based on lens/camera model)
        camera_fov = 185

        # Adjust horizon elevation using calibration polynomial
        elev = (camera_fov / 2) * (1 - (dot_radius / grid_radius))

        # Calculate Horizon Elevation
        horizon = (-0.00003 * (elev * elev)) + (1.0317 * (elev)) - 2.4902
        return (max([horizon, 0]))

    @staticmethod
    def radius_from_horizon(horizon, grid_radius):
        if not 0 <= horizon <= 90:
            raise ValueError("Horizon angle must be between 0 and 90 degrees")

        camera_fov = 185

        a = -0.00003
        b = 1.0317
        c = -2.4902 - horizon
        d = (b**2) - (4*a*c)
        sol1 = (-b-np.sqrt(d))/(2*a)
        sol2 = (-b+np.sqrt(d))/(2*a)
        sol = np.array([sol1, sol2])
        dot_radius = grid_radius *  (1 - 2 * sol / camera_fov)

        dot_radius = dot_radius[np.greater_equal(dot_radius, 0) * np.less_equal(dot_radius, grid_radius)]

        return np.asscalar(dot_radius)


class DefaultLens(Lens):
    """ Equirectangular projection"""

    NAME = "Equirectangular Projection (No Calibration)"
    INFO = """This assumes an equirectangular projection of the lens"""

    @staticmethod
    def horizon_from_radius(dot_radius, grid_radius):
        horizon = 90 * (1 - dot_radius / grid_radius)
        return horizon

    @staticmethod
    def radius_from_horizon(horizon, grid_radius):
        dot_radius = (90 - horizon) * grid_radius / 90
        return dot_radius

lenses = {lens.NAME:lens for lens in [SunexLens,
                                      DefaultLens]}