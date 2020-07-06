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


https://stats.stackexchange.com/questions/7977/how-to-generate-uniformly-distributed-points-on-the-surface-of-the-3-d-unit-sphe
sphere_sampler():


##
# https://stats.stackexchange.com/questions/7977/how-to-generate-uniformly-distributed-points-on-the-surface-of-the-3-d-unit-sphe
def hatbox_sampler(n):
    # create random sampling of a hemisphere
    z = random.uniform(-1, 1, n)
    theta = random.uniform(-np.pi , np.pi, n)
    x = np.sin(theta) * np.sqrt(1 - np.power(z, 2))
    y = np.cos(theta) * np.sqrt(1 - np.power(z, 2))
    r = np.sqrt(np.power(x, 2) + np.power(y, 2))
    h = np.degrees(np.arccos(r))

    return np.degrees(theta) % 360, h

n=50000
theta, hor = hatbox_sampler(n)

z = np.abs(z)

plt.hist(h, bins=np.arange(0, np.pi, 0.05))
plt.plot(np.arange(0,3, 0.05), np.cos(np.arange(0,3, 0.05))*2500)
plt.show()


