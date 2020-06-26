import numpy as np
from scipy.interpolate import interp1d
from pandas import DataFrame, read_csv
from shapely.geometry import LineString, Polygon, LinearRing, Point
from warnings import warn

from numpy import radians as ra

import matplotlib.pyplot as plt

try: # Python 3.x
    izip = zip
except:  # Python 2.7
    from itertools import izip


def add_sky_plot(figure, *args, **kwargs):
    ax = figure.add_subplot(*args, **kwargs, projection='polar')
    ax.set_theta_direction(-1)
    ax.set_theta_zero_location('N')
    ax.yaxis.set_visible(False)
    ax.set_ylim(0, 1)
    return ax
    
def plot_rotated_points(azi, hor, asp, dip, ax):
    rt = rotate_horizon(azi, hor, asp, dip)
    x = np.radians(rt[0])
    y = np.cos(np.radians(rt[1]))

    x[y < 0] = np.pi + x[y < 0]
    y[y < 0] = np.abs(y[y < 0])
    
    p = ax.plot(x, y, 'r-')
    #ax.plot(np.pi + rt[0][rt[1] > np.pi/2], np.abs(np.cos(rt[1][rt[1] > np.pi/2])), 'rx')
    return p
    
def SVF_discretized(az, hor, aspect, dip, increment=2, plot=False):
    """ 
    az1 = np.array(range(0,360,10))
    hor1 = az1 * 0 + 50
    SVF_discretized(az1, hor1, 130, 35, plot=True)
    """
    # rotate horizon coordinates
    rt = rotate_horizon(az, hor, aspect, dip)
    
    obs = test_obscured(rt[0], rt[1], increment)

    ## Plot cartesian
    xx = np.append(rt[0], obs)
    yy = np.append(rt[1], (obs * 0 + 90))
    yy = yy[np.argsort(xx)]
    xx = xx[np.argsort(xx)]
    
    # skyview: 
    # Create spline equation to obtain hor(az) for any azimuth
    # add endpoints on either side of sequence so interpolation is good 
    xx = np.concatenate((xx[-2:] - 360, xx, xx[:2] + 360)) 
    yy = np.concatenate((yy[-2:], yy, yy[:2]))
    FF = interp1d(x=xx, y=yy)

    if plot:
        fig = plt.figure()
        ax1 = fig.add_subplot(2,1,1)
        ax1.plot(xx,yy)
        
        # Plot sky
        ax = fig.add_subplot(2,1,2, projection='polar')
        ax.set_theta_direction(-1)
        ax.set_theta_zero_location('N')
        ax.yaxis.set_visible(False)
        ax.set_ylim(0, 1)
        ax.plot(ra(az), np.cos(ra(hor)))
        ax.plot(ra(rt[0]), np.cos(ra(rt[1])))
        
        # all pts
        ax.plot(ra(rt[0]), np.cos(ra(rt[1])), 'g.')
    
        # overhanging pts
        ax.plot(np.pi + ra(rt[0][rt[1] > 90]), np.abs(np.cos(ra(rt[1][rt[1] > 90]))), 'rx')
    
    return(sky_view_factor(FF, increment))

def sky_view_factor(f, delta_phi):
    """
    Calculates sky view factors using the discretized form of the continuum equation 
    for sky view factor (eq 9.3 from Helbig, 2009).  The integral form of the
    sky view equation is given in equation 4.41 of the same thesis.
    
    args:
        F a function that relates azimuth to horizon angle
        delta phi: discretized azimuth width
    """
    # Measure horizon at evenly spaced interval using spline
    phi = np.array(range(0, 360, delta_phi))
    theta_h = f(phi)
    
    # Check: don't allow horizons > 90 degrees that are opposite each other
    # This might not be a problem.
    theta_h = np.array([90 if y > 90 and f((x + 180) % 360) > 90 else y 
                                          for (x, y) in izip(phi, theta_h)])
    
    #don't allow negative horizon angles
    theta_h = np.max(np.row_stack((theta_h, theta_h * 0)), axis=0)
    
    # calculate cos2(theta)
    cos2theta = np.power(np.cos(ra(theta_h)), 2)
    
    # To deal with overhanging terrain, take negative cos2() if the horizon
    # is greater than 90. This might be wrong... But otherwise overhanging 
    # terrain increases the skyview factor
    S = [y if x <= 90 else -y for (x, y) in izip(theta_h, cos2theta)] 
    
    #print(DataFrame(zip(phi, theta_h, cos2theta, S)))
    F_sky = (delta_phi / 360.) * np.sum(S)
    F_sky = np.round(F_sky, decimals = 5)
    return(F_sky)
    

    
def SVF_from_csv(horizon_file, plot=False):
    horizon = read_csv(horizon_file)
    
    return

def rotation_matrix(axis, theta):
        """
        Return the rotation matrix associated with counterclockwise rotation about
        the given axis by theta radians (Euler-Rodrigues formula).
        
        v    = [0, 0, 2] #scanner data needs to be transposed
        axis = [0, 1, 0]
        theta = radians(90) #radian
    
        print(np.dot(rotation_matrix(axis,theta), v)) 
        """
        axis  = np.asarray(axis)
        theta = np.asarray(theta)
        axis  = axis / np.sqrt(np.dot(axis, axis))
        a = np.cos(theta / 2)
        b, c, d = -axis * np.sin(theta / 2)
        aa, bb, cc, dd = a*a, b*b, c*c, d*d
        bc, ad, ac, ab, bd, cd = b*c, a*d, a*c, a*b, b*d, c*d
        return np.array([[aa+bb-cc-dd, 2*(bc+ad), 2*(bd-ac)],
                        [2*(bc-ad), aa+cc-bb-dd, 2*(cd+ab)],
                        [2*(bd+ac), 2*(cd-ab), aa+dd-bb-cc]])
                        
def sphr_to_carte(theta, phi, r):
    """
    Convert from spherical coordinates to cartesian coordinates
    
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
    Convert from cartesian coordinates to spherical coordinates
    
    returns:
        (theta, phi, r)
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
    x = np.asarray(x)
    y = np.asarray(y)
    z = np.asarray(z)
    sph = carte_to_sphr(x, y, z)
    az = 90 - sph[0]  #sph[0] = theta
    az = az % 360
    hor = 90 - sph[1] # sph[1] = phi
    coords = np.array((az, hor))
    return(coords)
    
def rotate_towards(azimuth, rot_angle):
    """
    returns cartesian axis of rotation for azimuthal dip direction
    np.dot(rotmatrix, vector)
    """
    
    phi = ra(azimuth)
    x   = -np.cos(phi)
    y   = np.sin(phi)
    ax  = np.array([x, y, 0])
    
    # Calculate rotation matrix 
    rotmat = rotation_matrix(ax, ra(rot_angle))
    return(rotmat)
    
def test_overhang(theta, horiz):
    """
    for a set of horizon points, detects which ones are overhanging and returns 
    a list of True/False for whether the point is overhanging or not
    
    Args:
        theta: array or list of azimuthal directions
        horiz: array or list of horizon angles for each theta
    
    Returns:
        numpy array of logical values the same length as theta or horiz
    """
    # ensure inputs are arrays
    theta = np.asarray(theta)
    horiz = np.asarray(horiz)

    #project the horizon and azimuth onto the x-y plane
    xp = [np.cos(ra(h)) * np.cos(ra(90 - t)) for (t, h) in zip(theta, horiz)]
    yp = [np.cos(ra(h)) * np.sin(ra(90 - t)) for (t, h) in zip(theta, horiz)]
    
    # Draw out the horizon line object (we will test for intersections later)
    xy = np.array([[x,y] for (x,y) in zip(xp, yp)])
    L = LinearRing(xy)  # horizon line
    
    # Make on object for the origin
    O = Point([0,0])
    
    # Test each point: does a ray extending from the origin through the point 
    # intersect the horizon line once? twice?  If twice, is the point the nearest
    # or the farthest intersection?  This tells us whether or not its overhyng
    ohang = []
    
    for (x,y) in zip(xp, yp):
        pt_dist =  O.distance(Point([x,y])) # get length of segment  
        
        # make line in direction of point that has length 2 (so its sure to hit all other pts)
        l = LineString([[0,0], [x*(2/pt_dist),y*(2/pt_dist)]])
        
        # get intersection with horizon
        pts = l.intersection(L)
        if hasattr(pts, '__len__'): # for directions with more than one horizon value
            if len(pts) > 2:
                warn("A single azimuth has 3 or more horizon intersections, This"+ 
                "could be due to an overly complex horizon geometry and may lead"+
                "to unexpected behaviour", RuntimeWarning)
                
            # if there is another horizon line at a lower angle
            intersect_distances = [O.distance(x) for x in pts] #(distance ~ 1/angle)
            
            if not max([pt_dist] + intersect_distances) == pt_dist:
                ohang.append(True)
            else:
                ohang.append(False)
        
    # if only 1 intersection then not overhanging
        else: 
            ohang.append(False)

    return(np.array(ohang))

def test_obscured(theta, horiz, increment):
    """
    for a set of horizon points, detect which azimuth directions are completely
    overhung (i.e. x and (180 - x) both have 90 degree horizon angles)
    
    Args:
        theta: array or list of azimuthal directions
        horiz: array or list of horizon angles for each theta
    
    Returns:
        numpy array of logical values 
    """
    # ensure inputs are arrays
    theta = np.asarray(theta)
    horiz = np.asarray(horiz)
    
    #project the horizon and azimuth onto the x-y plane
    xp = [np.cos(ra(h)) * np.cos(ra(90 - t)) for (t, h) in zip(theta, horiz)]
    yp = [np.cos(ra(h)) * np.sin(ra(90 - t)) for (t, h) in zip(theta, horiz)]
    
    # Draw out the horizon line (we will test for intersections later)
    xy = np.array([[x,y] for (x,y) in zip(xp, yp)])
    L  = LinearRing(xy)  # horizon line
    
    obscura = []

    # make test points halfway around the circle ( 
    for angle in range(0,180, increment):

        # make line across horizon 
        x_test = 2 * np.cos(ra(90 - angle)) 
        y_test = 2 * np.sin(ra(90 - angle))
        l = LineString([[x_test, y_test], [-x_test, -y_test]])
        
        # get intersection with horizon
        pts = l.intersection(L)
        
        if pts:
            pass # intersects horizon at least once
        else:
            obscura.append(angle) # no intersection
            obscura.append( (180 + angle) % 360)

    return(np.array(obscura))

def rotate_horizon(az, hor, aspect, dip):
    """
    Calculates rotated horizon angles relative to a plane that is not necessarily
    horizontal 
    
    args:
        aspect: azimuth of plane
        dip: inclination of plane in direction of aspect
        
    Example:
        import numpy as np
        az1 = np.array(range(0,360,10))
        hor1 = (az1 * 0) + 30 
        rotated = rotate_horizon(az1, hor1, 135, 30)
    """

    # ensure inputs are arrays
    az = np.asarray(az)
    hor = np.asarray(hor)
    
    # change to cartesian coordinates and rotate
    cart_coords = horiz_to_carte(az, hor)
    rot_matrix = rotate_towards(aspect, -dip)
    rot = np.dot(rot_matrix, cart_coords)
    
    # put back in spherical coordinates
    coords = carte_to_horiz(rot[0], rot[1], rot[2])
    
    # put negative horizons at 0 degrees
    coords[1] = [x if x>=0 else 0 for x in coords[1]] 

    # for overhanging points, flip the azimuth
    overhanging = test_overhang(coords[0], coords[1])

    coords[0][overhanging] = (180 + coords[0][overhanging]) % 360
    coords[1][overhanging] = 180 - coords[1][overhanging]
    
    return(coords)
    


# def SVF_discretized(azi, hor, plane_az, plane_dip, delta_phi, 
#                     interpolation='linear'):
#     """
#     Calculates sky view factors using the discretized form of the continuum equation 
#     for sky view factor (eq 9.3 from Helbig, 2009).  The integral form of the
#     sky view equation is given in equation 4.41 of the same thesis.
#     
#     @param phi numpy array of azimuth 
#     
#     @param hor numpy array of horizon measurements with respect to a horizontal
#     plane (such as those recovered from the horizon camera )
#     
#     @param plane_az The azimuth of the surface for which SVF is to be
#     calculated (the direction of steepest descent)
#     
#     @param plane_dip The inclination of the surface for which SVF is to be
#     calculated
#     
#     @param delta_phi discretization interval of azimuth in degrees
#     
#     @param interpolation passed to interp1d()
#     """
#     # Ensure correct data structure and sort arrays based on azimuth
#     azi = np.array(azi) if type(azi) != np.ndarray and hasattr(azi, '__len__') else azi
#     hor = np.array(hor) if type(hor) != np.ndarray and hasattr(hor, '__len__') else hor
#     azi = azi[np.argsort(azi)]
#     hor = hor[np.argsort(azi)] # sorting to order by azimuth
#     
#     # Create spline equation to obtain hor(az) for any azimuth
#     # add endpoints on either side of sequence so interpolation is good 
#     x = np.concatenate((azi[-2:] - 360, azi, azi[:2] + 360)) 
#     y = np.concatenate((hor[-2:], hor, hor[:2]))
# 
#     f_hor = interp1d(x, y, kind = interpolation)
# 
#     # Measure horizon at evenly spaced interval using spline
#     phi = np.array(range(0, 360, delta_phi))
#     theta_h = f_hor(phi)
#     
#     # Check: don't allow horizons > 90 degrees that are opposite each other
#     # This might not be a problem.
#     theta_h = np.array([90 if y > 90 and f_hor((x + 180) % 360) > 90 else y 
#                                           for (x, y) in izip(phi, theta_h)])
#     
#     # Calculate adjusted horizon angles relative to (possibly) non-horizontal surface
#     theta_h_r = theta_h + angl_rotate(plane_dip, (phi - plane_az))
#     
#     #don't allow negative horizon angles
#     theta_h_r = np.max(np.row_stack((theta_h_r, theta_h_r * 0)), axis=0)
#     
#     # calculate cos2(theta)
#     cos2theta = np.power(np.cos(ra(theta_h_r)), 2)
#     
#     # To deal with overhanging terrain, take negative cos2() if the horizon
#     # is greater than 90. This might be wrong... But otherwise overhanging 
#     # terrain increases the skyview factor
#     S = [y if x <= 90 else -y for (x, y) in izip(theta_h_r, cos2theta)] 
#     
#     F_sky = (delta_phi / 360.) * np.sum(S)
#     
#     plt.polar(ra(phi), np.cos(ra(theta_h_r)))
#     plt.polar(ra(azi), np.cos(ra(hor)))
#     # plt.plot(phi, cos2theta)
#     # plt.plot(phi, S)
#     print(theta_h_r)
#     print([zip(azi, np.cos(ra(theta_h_r)))])
#     plt.show()
#     return(round(F_sky, 3))

# def angl_rotate(dip, rot):
#     """
#     Gives the angle relative to horizontal of a vector rotated from the 
#     direction of steepest decent.
#     
#     Can't deal with dips greater than 90 at the moment: The math stops working 
#     properly and I'm not sure how to fix it. ( ie. f(90,0) = 90, f(100,0) should 
#     be 100 but is actually equal to f(80,0).  
#     """
#     ## Don't allow dips > 90 degrees at the moment
#     if dip > 90:
#         raise ValueError("Dip must be between 0 and 90 degrees.")
#     
#     ## Handle different size vectors
#     if (not hasattr(dip, '__len__') == hasattr(rot, '__len__')):
#         if hasattr(rot, '__len__'):
#             dip = np.array([dip]*len(rot))
#             rot = np.array(rot) if type(rot) != np.ndarray else rot
#         else:
#             rot = np.array([rot]*len(dip))
#             dip = np.array(dip) if type(dip) != np.ndarray else dip
#     else:
#         if hasattr(dip, '__len__'):
#             if len(dip) != len(rot):
#                 raise ValueError("Vectors must be of equal length")
#             rot = np.array(rot) if type(rot) != np.ndarray else rot
#             dip = np.array(dip) if type(dip) != np.ndarray else dip
# 
#     ## Do calculation        
#     rotated_dip = (np.arcsin(np.sin(dip * np.pi / 180.) * np.cos(rot * np.pi / 180.))) 
#     rotated_dip *= (180. / np.pi)
#     rotated_dip = np.round(rotated_dip, 5)
#     
#     ## Account for dips greater than 90 degrees (overhanging surface)
#     
#     return(rotated_dip)  