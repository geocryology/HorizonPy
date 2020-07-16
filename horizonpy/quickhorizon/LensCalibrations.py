from abc import ABC, abstractmethod



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

    NAME = "Sunex Calibration"

    @staticmethod
    def horizon_from_radius(dot_radius, grid_radius):

        # Enter total field of view of Sunex camera (based on lens/camera model)
        camera = 185

        # Adjust horizon elevation using calibration polynomial
        elev = (camera/2) - ((dot_radius/grid_radius) * (camera/2))

        # Calculate Horizon Elevation
        elev = (-0.00003 * (elev * elev)) + (1.0317 * (elev)) - 2.4902
        return (max([elev, 0]))

    @staticmethod
    def radius_from_horizon():
        raise NotImplementedError


class DefaultLens(Lens):
    """ Equirectangular projection"""

    NAME = "Equirectangular (No Calibration)"

    @staticmethod
    def horizon_from_radius(dot_radius, grid_radius):
        horizon = 90 * (1 - dot_radius / grid_radius)
        return horizon

    @staticmethod
    def radius_from_horizon(horizon, grid_radius):
        dot_radius = (90 - horizon) * grid_radius / 90
        return dot_radius

lenses = {"Sunex" : SunexLens,
          "Default" : DefaultLens
         }