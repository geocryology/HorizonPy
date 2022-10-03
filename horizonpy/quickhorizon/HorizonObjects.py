from horizonpy.skyview import rotate_horizon, skyplot_figure, project_horizon_to_equirectangular
from matplotlib import pyplot as plt
import numpy as np

class HorizonPoint:

    def __repr__(self):
        return f"Horizon point at ({self.azimuth}, {self.horizon})"

    def __init__(self, azimuth, horizon):
        self._azimuth = azimuth
        self._horizon = horizon
        self._og_az = azimuth
        self._og_hor = horizon
        self.n1 = None
        self.n2 = None

    @property
    def azimuth(self):
        return self._azimuth

    @azimuth.setter
    def azimuth(self, value):
        self._azimuth = value % 360

    @property
    def horizon(self):
        return self._horizon

    @horizon.setter
    def horizon(self, value):
        self._horizon = value

    def set_coordinates(self, azimuth, horizon):
        self._azimuth = azimuth
        self._horizon = horizon

    def connect_from(self, hp: "HorizonPoint"):
        if hp in self.neighbours:
            return

        if not self.n2:
            self.n2 = hp

        else:
            raise RuntimeError("Already connected from")

    def connect(self, hp: "HorizonPoint"):
        if hp in self.neighbours:
            return

        if not self.n1:
            self.n1 = hp
            hp.connect_from(self)

        else:
            raise RuntimeError("Already connected to two other HorizonPoints")

    @property
    def neighbours(self):
        return [self.n1, self.n2]

    def rotate_view(self, aspect, dip):
        coords = rotate_horizon([self.azimuth], [self.horizon], aspect, dip, oob="")
        self.azimuth = coords[0][0]
        self.horizon = coords[1][0]

    def reset(self):
        self.horizon = self._og_hor
        self.azimuth = self._og_az

    def equirectangular(self):
        x, y = project_horizon_to_equirectangular([self.azimuth], [self.horizon])
        return x[0],y[0]

    def polar(self):
        x, y = self.equirectangular()
        r = np.sqrt(x**2 + y**2)
        azimuth = np.mod(np.arctan2(x,y), 2 * np.pi)
        return azimuth, r


class SkyPatch:
    """ a collection of horizon points that are connected in a loop """

    def __init__(self, *hp: HorizonPoint):
        self.hp = list(hp)

    def _validate(self):
        pass

    @classmethod
    def from_arrays(cls, azimuth, horizon):
        """ must be in proper order """
        pts = list()

        for a,h in zip(azimuth, horizon):
            hp = HorizonPoint(a, h)
            if pts:
                hp.connect(pts[-1])
            pts.append(hp)

        pts[0].connect(pts[-1])

        return cls(*pts)

    def rotate_view(self, aspect, dip):
        for hp in self.hp:
            hp.rotate_view(aspect, dip)

    def reset(self):
        for hp in self.hp:
            hp.reset()

    def plot(self):
        fig, ax = skyplot_figure()
        self.draw(ax)
        return fig, ax
    
    def draw(self, ax):
        coords = np.array([hp.polar() for hp in self.hp])
        theta = list(coords[:, 0]) + [coords[0, 0]]
        r = list(coords[:, 1]) + [coords[0, 1]]
        ax.plot(theta, r)

    def plot_rotated(self, aspect, dip):
        fig, ax = self.plot()
        self.rotate_view(aspect, dip)
        self.draw(ax)
        self.reset()

    def insert(self, where, hp):
        pass

    def coords_equirectangular(self):
        coords = np.array([p.equirectangular() for p in self.hp])
        x = list(coords[:, 0]) + [coords[0, 0]]
        y = list(coords[:, 1]) + [coords[0, 1]]
        return x, y

if __name__ == "__main__":
    h1 = HorizonPoint(10,20)
    h2 = HorizonPoint(20,25)
    h3 = HorizonPoint(30,40)
    S = SkyPatch.from_arrays([0,45,90,180,270], [11,12,13,14,15])
    import pandas as pd
    csv = pd.read_csv(r"C:\Users\Nick\src\HorizonPy\SampleHorizonImages\Horizon_1.hpt.csv")
    S = SkyPatch.from_arrays( csv["True Azimuth"], csv['Horizon'])
    a = np.arange(0,355, 5)
    h = np.zeros_like(a)
    S = SkyPatch.from_arrays( a, h)
    h1.connect(h2)
    h2.connect(h3)
    h3.connect(h1)
    S.plot_rotated(0,90)

    S.reset()
    circle1 = plt.Circle((0, 0), 1, color='r')
    fig, ax = plt.subplots()
    ax.set_xlim([-2, 2])
    ax.set_ylim([-2, 2])
    ax.add_patch(circle1)
    x,y = S.coords_equirectangular()
    ax.plot(x,y)
    S.rotate_view(0,109)
    x,y = S.coords_equirectangular()
    ax.plot(x,y)
    poly = Polygon(xy=list(zip(x,y)), facecolor='blue', alpha=0.2)
    ax.add_patch(poly)

    plt.show()