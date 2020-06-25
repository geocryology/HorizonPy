#hemisample py
from math import pi
from numpy import sin, cos, exp, sqrt, histogram, random, zeros_like
import numpy as np
import scipy.stats as st

class my_pdf(st.rv_continuous):
    
    def _pdf(self,x):
        return (pi/2.)*cos(pi*x/2.)  # Normalized over its range, in this case [0,1]

px =lambda(x): (pi/2.)*cos(pi*x/2.)
my_cv = my_pdf(a=0, b=1, name='my_pdf')
my_cv.rvs(size=3000)

class gaussian_gen(st.rv_continuous):
    "Gaussian distribution"
    def _pdf(self, x):
        return exp(-x**2 / 2.) / sqrt(2.0 * pi)

gaussian = gaussian_gen(name='gaussian')

def rejection_sampler(p,xbounds,pmax):
    while True:
        x = np.random.rand(1)*(xbounds[1]-xbounds[0])+xbounds[0]
        y = np.random.rand(1)*pmax
        if y <= p(x):
            return x