#hemisample py
# For even sampling over a hemisphere
from math import pi
from numpy import sin, cos, exp, sqrt, histogram, random, zeros_like
import numpy as np
import scipy.stats as st
import numpy as np


class my_pdf(st.rv_continuous):

    def _pdf(self,x):
        return (pi/2.)*cos(pi*x/2.)  # Normalized over its range, in this case [0,1]

px =lambda x: (pi/2.)*cos(pi*x/2.)

my_cv = my_pdf(a=0, b=1, name='my_pdf')
z = my_cv.rvs(size=3000)

plt.hist(z, bins=np.arange(0, 1, 0.05))
plt.plot(np.arange(0,3, 0.05), np.cos(np.arange(0,3, 0.05)*(2*np.pi)/4)*200);plt.show()

class gaussian_gen(st.rv_continuous):
    "Gaussian distribution"
    def _pdf(self, x):
        return exp(-x**2 / 2.) / sqrt(2.0 * pi)

gaussian = gaussian_gen(name='gaussian')

def rejection_sampler(p, xbounds, pmax):
    while True:
        x = np.random.rand(1) * (xbounds[1] - xbounds[0]) + xbounds[0]
        y = np.random.rand(1) * pmax
        if y <= p(x):
            return x



# https://stats.stackexchange.com/questions/7977/how-to-generate-uniformly-distributed-points-on-the-surface-of-the-3-d-unit-sphe
def hatbox_sampler(n, planar = False):
    # create random sampling of a hemisphere
    # returns azimuth and horizon in degrees.
    # theta, hor = hatbox_sampler(10000)
    # plt.hist(theta, bins=np.arange(1,360,1 ));plt.show()
    # plt.hist(hor, bins = np.arange(1,90,1))
    # plt.plot(np.arange(0, 90, 1), np.cos(np.arange(0, 90, 1)*(2*np.pi)/360)*sin(np.radians(1))*100000/2)
    # plt.show()

    z = random.uniform(-1, 1, n)
    theta = random.uniform(-np.pi , np.pi, n)
    x = np.sin(theta) * np.sqrt(1 - np.power(z, 2))
    y = np.cos(theta) * np.sqrt(1 - np.power(z, 2))

    if planar:
        return x, y
    else:
        r = np.sqrt(np.power(x, 2) + np.power(y, 2))
        h = np.degrees(np.arccos(r))

        return np.degrees(theta) % 360, h

    # check equirectangular vs. top-down


# import pandas as pd
# from shapely.geometry import LineString, Polygon, LinearRing, Point, MultiPoint
#
# df = pd.read_csv(r"C:\Users\Nick\src\HorizonPy\SampleHorizonImages\Horizon_3.hpt.csv")
# df = df.drop(['X','Y','Image Azimuth'], axis=1)
# df = df.append(df.iloc[0,:])
# df = df.reset_index()
# # project onto plane
# df['m'] = np.cos(np.radians(df['Horizon']))
# df['me'] = 2 * np.radians(90 - df['Horizon']) / np.pi
#
# df['X'] = np.cos(np.radians(df['True Azimuth'])) * df['m']
# df['Y'] = np.sin(np.radians(df['True Azimuth'])) * df['m']
#
# # equirect
# df['Xe'] = np.cos(np.radians(df['True Azimuth'])) * df['me']
# df['Ye'] = np.sin(np.radians(df['True Azimuth'])) * df['me']
#
#
# # create polygon
# P = Polygon(p for p in zip(df['X'], df['Y']))
#
# # make random points
# th, hr = hatbox_sampler(5000, True)
#
# # create Multipoint
# rdm = MultiPoint([p for p in zip(th, hr)])
#
# # test intersection
# int = pd.Series([p.intersects(P) for p in rdm])
#
# plt.plot(th[int], hr[int], 'g.')
# plt.plot(th[~int], hr[~int], 'r.')
# plt.show()
#
#
# plt.plot(th, hr, 'g.')
# plt.plot(df['X'], df['Y'], 'r')
# plt.plot(df['Xe'], df['Ye'], 'b')
# plt.show()
#
#
# plt.plot(*P.exterior.xy)
# Polygon()
#
# plt.plot()
#
# def skyview_stochastic(horizon, azimuth, n):
#     if not (horizon[0] == horizon[-1] and azimuth[0] == azimuth[-1]):
#         horizon = np.append(horizon, horizon[0])
#         azimuth = np.append(azimuth, azimuth[0])
#
#     # Project horizon points onto plane (should this be equirectangular?)
#     r = np.cos(np.radians(horizon)) # 2*np.radians(90-horizon) / np.pi
#     sky_x = np.cos(np.radians(azimuth)) * r
#     sky_y = np.sin(np.radians(azimuth)) * r
#
#     # make sky polygon
#     P = Polygon(p for p in zip(horizon, azimuth))
#
#     # generate random sampling points
#     x, y = hatbox_sampler(n, planar=True)
#     pts = MultiPoint([p for p in zip(x, y)])
#
#     # find intersecting points
#     int = pd.Series([p.intersects(P) for p in rdm])
#
#
#
#
#
#
#     # generate random sampling points and project (equirectangular)
#     th_s, hr_s = hatbox_sampler(m, planar=False)
#     r_s =  (90 - hr_s) / 90
#     sample_x = np.cos(np.radians(th_s)) * r_s
#     sample_y = np.sin(np.radians(th_s)) * r_s
#
#     pts = MultiPoint([p for p in zip(sample_x, sample_y)])
#
#     # find intersecting points
#     int = pd.Series([p.intersects(P) for p in rdm])
#
#
#     x = list()
#
#     for i in np.arange(1, n+1):
#         ti =
#         pi =
#         z = np.sin(np.pi * (2 * i-1) / (2 * n)) * (/)
#         x.append(z)
#
#     svf =
#     return sum(x) * np.pi/(2*n)
#
#

