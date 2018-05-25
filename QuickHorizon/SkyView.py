import numpy as np
from scipy.interpolate import interp1d
from itertools import izip
from pandas import DataFrame, read_csv

from numpy import radians as ra
#
import matplotlib.pyplot as plt

def SVF_discretized(azi, hor, plane_az, plane_dip, delta_phi, 
                    interpolation='linear',allow_negative_horizon=False):
    """
    Calculates sky view factors using the discretized form of the continuum equation 
    for sky view factor (eq 9.3 from Helbig, 2009).  The integral form of the
    sky view equation is given in equation 4.41 of the same thesis.
    
    @param phi numpy array of azimuth 
    
    @param hor numpy array of horizon measurements with respect to a horizontal
    plane (such as those recovered from the horizon camera )
    
    @param plane_az The azimuth of the surface for which SVF is to be
    calculated (the direction of steepest descent)
    
    @param plane_dip The inclination of the surface for which SVF is to be
    calculated
    
    @param delta_phi discretization interval of azimuth in degrees
    
    @param interpolation passed to interp1d()
    """
    # Ensure correct data structure and sort arrays based on azimuth
    azi = np.array(azi) if type(azi) != np.ndarray and hasattr(azi, '__len__') else azi
    hor = np.array(hor) if type(hor) != np.ndarray and hasattr(hor, '__len__') else hor
    azi = azi[np.argsort(azi)]
    hor = hor[np.argsort(azi)] # sorting to order by azimuth
    
    # Create spline equation to obtain hor(az) for any azimuth
    # add endpoints on either side of sequence so interpolation is good 
    x = np.concatenate((azi[-2:] - 360, azi, azi[:2] + 360)) 
    y = np.concatenate((hor[-2:], hor, hor[:2]))

    f_hor = interp1d(x, y, kind = interpolation)

    # Measure horizon at evenly spaced interval using spline
    phi = np.array(range(0, 360, delta_phi))
    theta_h = f_hor(phi)
    
    # Check: don't allow horizons > 90 degrees that are opposite each other
    # This might not be a problem.
    theta_h = np.array([90 if y > 90 and f_hor((x + 180) % 360) > 90 else y 
                                          for (x, y) in izip(phi, theta_h)])
    
    # Calculate adjusted horizon angles relative to (possibly) non-horizontal surface
    theta_h_r = theta_h + angl_rotate(plane_dip, (phi - plane_az))
    
    #don't allow negative horizon angles
    if not allow_negative_horizon:
        theta_h_r = np.max(np.row_stack((theta_h_r, theta_h_r * 0)), axis=0)
    cos2theta = np.power(np.cos(ra(theta_h_r)), 2)
    
    # To deal with overhanging terrain, take negative cos2() if the horizon
    # is greater than 90. This might be wrong... But otherwise overhanging 
    # terrain increases the skyview factor
    S = [y if x <= 90 else -y for (x, y) in izip(theta_h_r, cos2theta)] 
    
    F_sky = (delta_phi / 360.) * np.sum(S)
    
    plt.polar(ra(phi), np.cos(ra(theta_h_r)))
    plt.polar(ra(azi), np.cos(ra(hor)))
    # plt.plot(phi, cos2theta)
    # plt.plot(phi, S)
    print(theta_h_r)
    print([zip(azi, np.cos(ra(theta_h_r)))])
    plt.show()
    return(round(F_sky, 3))


    
def angl_rotate(dip, rot):
    """
    Gives the angle relative to horizontal of a vector rotated from the 
    direction of steepest decent.
    
    Can't deal with dips greater than 90 at the moment: The math stops working 
    properly and I'm not sure how to fix it. ( ie. f(90,0) = 90, f(100,0) should 
    be 100 but is actually equal to f(80,0).  
    """
    ## Don't allow dips > 90 degrees at the moment
    if dip > 90:
        raise ValueError("Dip must be between 0 and 90 degrees.")
    
    ## Handle different size vectors
    if (not hasattr(dip, '__len__') == hasattr(rot, '__len__')):
        if hasattr(rot, '__len__'):
            dip = np.array([dip]*len(rot))
            rot = np.array(rot) if type(rot) != np.ndarray else rot
        else:
            rot = np.array([rot]*len(dip))
            dip = np.array(dip) if type(dip) != np.ndarray else dip
    else:
        if hasattr(dip, '__len__'):
            if len(dip) != len(rot):
                raise ValueError("Vectors must be of equal length")
            rot = np.array(rot) if type(rot) != np.ndarray else rot
            dip = np.array(dip) if type(dip) != np.ndarray else dip

    ## Do calculation        
    rotated_dip = (np.arcsin(np.sin(dip * np.pi / 180.) * np.cos(rot * np.pi / 180.))) 
    rotated_dip *= (180. / np.pi)
    rotated_dip = np.round(rotated_dip, 5)
    
    ## Account for dips greater than 90 degrees (overhanging surface)
    
    return(rotated_dip)  
    
def SVF_from_geotop():
    pass

def rotation_matrix(axis, theta):
        """
        Return the rotation matrix associated with counterclockwise rotation about
        the given axis by theta radians (Euler-Rodrigues formula).
        
        v = [0, 0, 2] #scanner data needs to be transposed
        axis = [0, 1, 0]
        theta = radians(90) #radian
    
        print(np.dot(rotation_matrix(axis,theta), v)) 
        """
        axis  = np.asarray(axis)
        theta = np.asarray(theta)
        axis  = axis/sqrt(np.dot(axis, axis))
        a = cos(theta/2)
        b, c, d = -axis*sin(theta/2)
        aa, bb, cc, dd = a*a, b*b, c*c, d*d
        bc, ad, ac, ab, bd, cd = b*c, a*d, a*c, a*b, b*d, c*d
        return np.array([[aa+bb-cc-dd, 2*(bc+ad), 2*(bd-ac)],
                        [2*(bc-ad), aa+cc-bb-dd, 2*(cd+ab)],
                        [2*(bd+ac), 2*(cd-ab), aa+dd-bb-cc]])
                        
def sphr_to_carte(theta, phi, r):
    """
    theta: angle from x axis in XY plane
    phi: angle from z axis (note that horizon = 90 - phi)
    q = sphr_to_carte([0,30], [10,10], [1,1])
    """
    theta = np.asarray(theta)
    phi = np.asarray(phi)
    r = np.asarray(r)
    
    theta = theta % 360
    if not all((0 <= phi) * (phi < 180)):
        raise ValueError("phi must be between 0 and 180 degrees")

    x = r*np.sin(ra(phi))*np.cos(ra(theta))
    y = r*np.sin(ra(phi))*np.sin(ra(theta))
    z = r*np.cos(ra(phi))
    coords = np.array((x,y,z))
    return(coords)
    
def carte_to_sphr(x, y, z, deg=True):
    """
    theta: angle from x axis in XY plane (increasing from positive X to positive Y)
    phi: angle from z axis (note that horizon = 90 - phi)
    
    """
    r = np.sqrt(np.power(x,2) + np.power(y,2) + np.power(z,2))
    theta = np.arctan2(y, x)  # this is fishy - only works when variables are in opposite order
    #theta = np.arctan(y / x)
    phi = np.arccos(z / r)
    #phi = np.arctan(np.sqrt(np.power(x, 2) + np.power(y, 2)) / z)
    #phi = np.arctan2(z, np.sqrt(np.power(x, 2) + np.power(y, 2)))
    if deg:
        theta = np.degrees(theta)
        theta = theta % 360
        phi = np.degrees(phi)
    coords = np.array((theta, phi, r))
    return(coords)

def horiz_to_carte(az, hor):
    """
    returns cartesian coordinates from a horizon angle and azimuth
    q=horiz_to_carte([0,30], [10,10], [1,1])
    """
    az = np.asarray(az)
    hor = np.asarray(hor)
    az[hor > 90] = az[hor > 90] + 180
    hor[hor > 90] = 180 - hor[hor > 90]
    az = az % 360
    r = az * 0 + 1  # assume unit radius
    theta = 90 - az 
    phi = 90 - hor
    coords = sphr_to_carte(theta, phi, r)
    return(coords)  

def carte_to_horiz(x, y, z):
    """
    returns horizon angle and azimuth from cartesian coordinates
    q=horiz_to_carte([0,30], [10,10], [1,1])
    
    """
    sph = carte_to_sphr(x,y,z)
    az = 90 - sph[0]  #sph[0] = theta
    az = az % 360
    hor = 90 - sph[1] # sph[1] = phi
    coords = np.array(az, hor)
    return(coords)
    
def dip_towards(azimuth, dip):
    """
    returns cartesian axis of rotation for azimuthal dip direction
    np.dot(rotmatrix, vector)
    """
    phi = ra(azimuth)
    x = -np.cos(phi)
    y = np.sin(phi)
    ax = np.array([x,y,0])
   #return(ax)
    rotmat = rotation_matrix(ax, ra(dip))
    return(rotmat)
    
## putting in larger values screws things up
# rotate 90, 30 by 

carte_to_sphr([.5], [-.5], [-sqrt(2)/2])
carte_to_sphr([0.35355339],  [0.35355339],  [0.8660254])

carte_to_sphr(0.5, 0, sqrt(3)/2)

s = np.array([0, 91, 1])
a = sphr_to_carte([s[0]], [s[1]], [s[2]])
carte_to_sphr(a[0], a[1], a[2])

s = [45, 45, 1]
a = sphr_to_carte(s[0], s[1], s[2])
carte_to_sphr(a[0], a[1], a[2])

s = [-30, 120, 1]
a = sphr_to_carte(s[0], s[1], s[2])
carte_to_sphr(a[0], a[1], a[2])

s = [120, 120, 1]
a = sphr_to_carte(s[0], s[1], s[2])
carte_to_sphr(a[0], a[1], a[2])

def getsame(theta, phi, verbose=False):
    C = sphr_to_carte(theta, phi, 1)
    if verbose:
        print(C)
    S = carte_to_sphr(C[0], C[1], C[2])
    return(S)
    
def getsame(theta, phi, verbose=False):
    C = horiz_to_carte(theta, phi)
    if verbose:
        print(C)
    S = carte_to_horiz(C[0], C[1], C[2])
    return(S)

def check_conversion():
    for i in range(0,360,20):
        for j in range(0,180,20):
            S = getsame(i,j)
            if not all((S - np.array([i,j,1])) <.001 ):
                print(np.array([i,j,1]))
                print(S)
                print(S - np.array([i,j,1]))

check_conversion()
        
carte_to_sphr(a[0], a[1], a[2])
carte_to_horiz(a[0], a[1], a[2])

a = sphr_to_carte(0, 90, 1)
b = rotation_matrix([0,1,0], -ra(30))
c = np.dot(b,a)
carte_to_sphr(c[0], c[1], c[2])



a = horiz_to_carte(30, 30)
b = dip_towards(30, 100)
c = np.dot(a,b)
carte_to_horiz(c[0], c[1], c[2])


az1 = np.array(range(0,360,60))
hor1 = az * 0 + 30

a = [horiz_to_carte(x, y) for (x,y) in izip(az1, hor1)]
plt.plot(
def rotate_horizon(az, hor, aspect, dip):
    a = horiz_to_carte(90, 60)

sphr_to_carte(0,60,1) == horiz_to_carte(90,60)


sphr_to_carte(0,30,1) == horiz_to_carte(90,60)
#     
# import matplotlib.pyplot as plt
# h=[80,0,160,240,320]
# az=[20,20,20,20,20]
# a=SVF_discretized(h, az, 80,30,1, 'linear')
# plt.plot(a['a'][0],a['a'][1])
# plt.plot(a['b'][0],a['b'][1])
# plt.plot(a['c'][0],a['c'][1])
# plt.plot(a['c'][0],a['c'][2])
# 
# b=SVF_discretized(h, az, 90,20,1, 'linear')
# plt.plot(b['c'][0],b['c'][2])
# 
# c=SVF_discretized(h, az, 190,20,1, 'linear')
# plt.plot(c['c'][0],c['c'][2])
# # plt.plot(b[0],b[1])
# # plt.plot(b[0],b[2])
# # 
# # n=1
# # a=SVF_discretized(range(0,360,n), [50]*(360/n), 0,60,1, 'cubic')
# # plt.plot(a[0],a[1])
# # plt.plot(a[0],a[2])
# # b=SVF_discretized(range(0,360,n), [50]*(360/n), 90,60,1, 'cubic')
# # plt.plot(b[0],b[1])
# # plt.plot(b[0],b[2])
# # from pandas import DataFrame as df
# # #q = df(a['z'])
# # angl_rotate(30, [80,0,160,240,320])
# # 
# SVF_discretized([80,0,160,240,320], [50,50,50,50,50], 20,0,1, 'cubic')
# SVF_discretized([80,0,160,240,320], [50,50,50,50,50], 40,0,1, 'cubic')
# SVF_discretized([80,0,160,240,320], [50,50,50,50,50], 80,0,1, 'cubic')
# # 
# # # same dip different azimuth should give same but doesnt'
# SVF_discretized([80,0,160,240,320], [50,50,50,50,50], 20,40,1, 'cubic')
# SVF_discretized([80,0,160,240,320], [50,50,50,50,50], 40,40,1, 'cubic')
# SVF_discretized([80,0,160,240,320], [50,50,50,50,50], 340,40,1, 'cubic')
# 
# SVF_discretized([80,0,160,240,320], [50,40,30,30,40], 20,40,1, 'cubic')
# SVF_discretized([80,0,160,240,320], [50,40,30,30,40], 40,40,1, 'cubic')
# SVF_discretized([80,0,160,240,320], [50,40,30,30,40], 340,40,1, 'cubic')
# 
# # should decrease with tilt
az1 = np.array(range(0, 360, 2))
hor1 = np.array([0 if 90 <= x <= 270 else 60 for x in az1])
SVF_discretized(az1, hor1, 0,0,1, 'linear')
SVF_discretized(az1, hor1, 90,60,1, 'linear')
SVF_discretized(az1, hor1, 90,30,1, 'linear')
SVF_discretized(az1, hor1, 55,30,1, 'linear')
SVF_discretized(az1, hor1, 0,90,1, 'linear')
# # 
# # 
# 
hor2 = az1 * 0 + 40
hor2 = [0 if 0 <= az < 90 else 90 for az in az1]
# 
# 
SVF_discretized(az1, hor2, 0,0,1, 'cubic')
SVF_discretized(az1, hor2, 0,45,1, 'cubic')
 SVF_discretized(az1, hor2, 0,60,1, 'cubic')
# SVF_discretized(az1, hor2, 0,95,1, 'cubic')


# ## SVF calculation now performs the interpolation first, and then rotates the 
# ## interpolated coordinates so that the rotated vectors don't change depending 
# ## the surface azimuth.  For very sparse discretization ponts, this is still 
# ## a problem.
# 
# ## where are these negative horizon angles coming from?
# ## - usually, the minimum horizon in a direction would be the horizon
# ## of the plane, in the fake example it doesn't work that way.
# ## In any case, negative horizon angles (open sky below 0 degrees) has been 
# ## prohibited (can toggle on/off though)
# 
# # when the angl_rotate dip is greater than 90
# # dip = 90-dip & angle is 90 - result