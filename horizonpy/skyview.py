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
    
def plot_rotated_points(az, hor, asp, dip, ax):
    
    rt = rotate_horizon(az, hor, asp, dip)
    
    x = np.radians(rt[0])[np.argsort(rt[0])]
    y = np.cos(np.radians(rt[1]))[np.argsort(rt[0])]

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
    
    return(svf_helbig_2009(FF, increment))

def svf_helbig_2009(f, delta_phi):
    """
    Calculates sky view factors using the discretized form of the continuum equation 
    for sky view factor (eq 9.3 from Helbig, 2009).  The integral form of the
    sky view equation is given in equation 4.41 of the same thesis.
    
    args:
        f a function that relates azimuth to horizon angle
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
    
    F_sky = (delta_phi / 360.) * np.sum(S)
    F_sky = np.round(F_sky, decimals = 5)
    return(F_sky)
      

def annulus(r_in, r_out):
    C1 = Point(0,0).buffer(r_in)
    C2 = Point(0,0).buffer(r_out)
    return C2.difference(C1)

def project_horizon_to_equirectangular(azimuth, horizon, r0=1, degrees=True):
    if degrees:
        azimuth = np.radians(azimuth)
        r =  (90 - horizon) * r0 / 90
    else:
        r =  (np.pi / 2 - horizon) * r0 / (np.pi/2)
    x = np.cos(azimuth) * r
    y = np.sin(azimuth) * r
    
    return x,y   
    

# Steyn -
def svf_steyn_1980(azimuth, horizon, n=36):
    if not (horizon[0] == horizon[-1] and azimuth[0] == azimuth[-1]):
        horizon = np.append(horizon, horizon[0])
        azimuth = np.append(azimuth, azimuth[0])

    sky_x, sky_y = project_horizon_to_equirectangular(azimuth, horizon)

    # make sky polygon
    P = Polygon(p for p in zip(sky_x, sky_y))

    L = list()

    for i in np.arange(1, n+1):
        # Calculate sky proportion of each annulus
        A = annulus((i-1)/n, (i)/n )
        ti = A.area
        pi = P.intersection(A).area
        annular_svf = np.sin(np.pi * (2 * i-1) / (2 * n)) * (pi / ti)
        L.append(annular_svf)

    F_sky = sum(L) * np.pi/(2*n)
    F_sky = np.round(F_sky, 5)
    return F_sky
    
    
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

def project_horizon_top_down(azimuth, horizon, r0=1, degrees=True):
    if degrees:
        azimuth = np.radians(azimuth)
        horizon = np.radians(horizon)

    offset = np.pi / 2
        
    x = np.cos(horizon) * np.cos(offset - azimuth)
    y = np.cos(horizon) * np.sin(offset - azimuth) 
    
    return x,y   

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
    xp, yp = project_horizon_top_down(theta, horiz)
    
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
    
    # put negative horizons at 0 degrees (Assume self-shading)
    coords[1] = [x if x>=0 else 0 for x in coords[1]] 

    # for overhanging points, flip the azimuth
    overhanging = test_overhang(coords[0], coords[1])

    coords[0][overhanging] = (180 + coords[0][overhanging]) % 360
    coords[1][overhanging] = 180 - coords[1][overhanging]
    
    return(coords)
    

