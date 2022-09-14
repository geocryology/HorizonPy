import numpy as np
from scipy.interpolate import interp1d
from pandas import DataFrame, read_csv
from shapely.geometry import LineString, Polygon, LinearRing, Point
from warnings import warn

import matplotlib.pyplot as plt

try: # Python 3.x
    izip = zip
except:  # Python 2.7
    from itertools import izip


def SVF_discretized(azimuth, horizon, aspect, dip, increment=2):
    """
    az1 = np.array(range(0,360,10))
    hor1 = az1 * 0 + 50
    SVF_discretized(az1, hor1, 130, 35, plot=True)
    """
    # rotate horizon coordinates
    rt = rotate_horizon(azimuth, horizon, aspect, dip)

    # for overhanging points, flip the azimuth
    overhanging = test_overhang(rt[0], rt[1])

    rt[0][overhanging] = (180 + rt[0][overhanging]) % 360
    rt[1][overhanging] = 180 - rt[1][overhanging]

    obs = test_obscured(rt[0], rt[1], increment)

    xx = np.append(rt[0], obs)
    yy = np.append(rt[1], (obs * 0 + 90))
    yy = yy[np.argsort(xx)]
    xx = xx[np.argsort(xx)]

    # skyview:
    # Create spline equation to obtain horizon(azimuth) for any azimuth
    # add endpoints on either side of sequence so interpolation is good
    xx = np.concatenate((xx[-2:] - 360, xx, xx[:2] + 360))
    yy = np.concatenate((yy[-2:], yy, yy[:2]))

    FF = interp1d(x=xx, y=yy)
    F_sky = svf_helbig_2009(FF, increment)

    return(F_sky)


def svf_helbig_2009(f, delta_phi=1):
    """Calculate sky view factor by integrating over all azimuths

    Uses the discretized form of the continuum equation
    for sky view factor (eq 9.3 from Helbig, 2009).  The integral form of the
    sky view equation is given in equation 4.41 of the same thesis.

    Parameters
    ----------
    f : function
        function relating azimuth to horizon angle
    delta_phi : int
        discretized azimuth width in degrees

    Returns
    -------
    float
        Sky view factor between 0 and 1

    Examples
    --------
    >>> delta_phi = 1
    >>> f = lambda phi : 0 * phi
    >>> svf_helbig_2009(f, delta_phi)
    1.0
    >>> f = lambda phi : 0 * phi + 30
    >>> svf_helbig_2009(f, delta_phi)
    0.75


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
    cos2theta = np.power(np.cos(np.radians(theta_h)), 2)

    # To deal with overhanging terrain, take negative cos2() if the horizon
    # is greater than 90. This might be wrong... But otherwise overhanging
    # terrain increases the skyview factor
    S = [y if x <= 90 else -y for (x, y) in izip(theta_h, cos2theta)]

    F_sky = (delta_phi / 360.) * np.sum(S)
    F_sky = np.round(F_sky, decimals = 5)
    return(F_sky)


def annulus(r_in, r_out):
    """ Create an annulus

    Parameters
    ----------
    r_in, r_out : float
        inner and outer radius of annulus

    Returns
    -------
        Shapely Polygon object

    Example
    -------
    >>> A = annulus(1,2)
    >>> A.area
    9.409645471637816
    """
    C1 = Point(0,0).buffer(r_in)
    C2 = Point(0,0).buffer(r_out)
    return C2.difference(C1)


def svf_steyn_1980(azimuth, horizon, n=36):
    """ Calculate sky view factor using method of annuli

    Parameters
    ----------
    azimuth : array_like
        Array of horizon angles in degrees
    horizon : array_like
        Array of horizon angles in degrees

    Returns
    -------
    float
        Sky view factor between 0 and 1

    Examples
    --------
    >>> import numpy as np
    >>> azimuth = np.arange(0, 360, 10)
    >>> horizon = azimuth * 0
    >>> svf_steyn_1980(azimuth, horizon, n=18)
    1.00102
    >>> svf_steyn_1980(azimuth, horizon, n=36)
    1.00019
    >>> svf_steyn_1980(azimuth, horizon, n=100)
    1.0

    """
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


def rotation_matrix(axis, theta):
    """ Create a rotation matrix

    Return the rotation matrix associated with counterclockwise rotation about
    a given axis by theta radians (Euler-Rodrigues formula).

    Parameters
    ----------
    axis : array_like
        3-d vector specifying axis around which to rotate
    theta : float
        angle of rotation in radians

    Returns
    -------
    array
        3 x 3 rotation matrix

    Examples
    --------
    >>> import numpy as np
    >>> v    = [[0,2],[0,0],[2,0]] #[[0, 0, 2], [2, 0, 0]] # data to be rotated
    >>> axis = [0, 1, 0]
    >>> theta = np.radians(90)
    >>> np.dot(rotation_matrix(axis,theta), v)
    array([[ 2.,  0.],
           [ 0.,  0.],
           [ 0., -2.]])
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
    """ Convert from spherical coordinates to cartesian coordinates

    Parameters
    ----------
    theta : array_like
        angle from x axis in XY plane in radians
    phi : array_like
        angle from z axis (note that horizon = 90 - phi)
    r : array_like
        radius

    Returns
    -------
    array
        coordinates in cartesian space

    Examples
    --------
    >>> sphr_to_carte([0,45,90], [0,30,45], [1,1,1])
    array([[0.00000000e+00, 3.53553391e-01, 4.32978028e-17],
           [0.00000000e+00, 3.53553391e-01, 7.07106781e-01],
           [1.00000000e+00, 8.66025404e-01, 7.07106781e-01]])
    """
    theta = np.asarray(theta)
    phi = np.asarray(phi)
    r = np.asarray(r)

    theta = theta % 360
    if not all((0 <= phi) * (phi < 180)):
        raise ValueError("phi must be between 0 and 180 degrees")

    x = r*np.sin(np.radians(phi))*np.cos(np.radians(theta))
    y = r*np.sin(np.radians(phi))*np.sin(np.radians(theta))
    z = r*np.cos(np.radians(phi))
    coords = np.array((x,y,z))
    return(coords)


def carte_to_sphr(x, y, z, degrees=True):
    """
    Convert from cartesian coordinates to spherical coordinates

    Parameters
    ----------
    x,y,z : array_like
        coordinates in cartesian space
    degrees : whether output should be in degrees

    Returns
    -------
    array
         spherical coordinates (theta, phi, r)

    """
    r = np.sqrt(np.power(x,2) + np.power(y,2) + np.power(z,2))
    theta = np.arctan2(y, x)  # this is fishy - variables  in opposite order as expected (because you're looking up at the sky?)
    #theta = np.arctan(y / x)
    phi = np.arccos(z / r)
    #phi = np.arctan(np.sqrt(np.power(x, 2) + np.power(y, 2)) / z)
    #phi = np.arctan2(z, np.sqrt(np.power(x, 2) + np.power(y, 2)))
    if degrees:
        theta = np.degrees(theta)
        theta = theta % 360
        phi = np.degrees(phi)
    coords = np.array((theta, phi, r))
    return(coords)


def horiz_to_carte(azimuth, horizon):
    """
    returns cartesian coordinates from a horizon angle and azimuth
    q=horiz_to_carte([0,30], [10,10], [1,1])
    """
    azimuth = np.asarray(azimuth)
    horizon = np.asarray(horizon)
    azimuth[horizon > 90] = azimuth[horizon > 90] + 180
    horizon[horizon > 90] = 180 - horizon[horizon > 90]
    azimuth = azimuth % 360
    r = azimuth * 0 + 1  # assume unit radius
    theta = 90 - azimuth
    phi = 90 - horizon
    coords = sphr_to_carte(theta, phi, r)
    return(coords)


def carte_to_horiz(x, y, z):
    """
    returns horizon angle and azimuth from cartesian coordinates

    Parameters
    ----------
    x,y,z :
        coordinates in cartesian space

    Returns
    -------
    array
        coordinates as azimuth-horizon pairs

    Examples
    --------
    >>> carte_to_horiz([0,30], [10,10], [1,1])
    array([[ 0.        , 71.56505118],
           [ 5.71059314,  1.81124805]])
    """
    x = np.asarray(x)
    y = np.asarray(y)
    z = np.asarray(z)

    sph = carte_to_sphr(x, y, z)
    azimuth = 90 - sph[0]  #sph[0] = theta
    azimuth = azimuth % 360
    horizon = 90 - sph[1] # sph[1] = phi
    coords = np.array((azimuth, horizon))

    return(coords)


def rotate_towards(azimuth, rot_angle):
    """
    returns cartesian axis of rotation for azimuthal dip direction
    np.dot(rotmatrix, vector)
    """

    phi = np.radians(azimuth)
    x   = -np.cos(phi)
    y   = np.sin(phi)
    ax  = np.array([x, y, 0])

    # Calculate rotation matrix
    rotmat = rotation_matrix(ax, np.radians(rot_angle))
    return(rotmat)


def rotate_horizon(azimuth, horizon, aspect, dip):
    """
    Calculates rotated horizon angles relative to a plane

    Parameters
    ----------
        azimuth : array_like
            Array of horizon angles in degrees
        horizon : array_like
            Array of horizon angles in degrees
        aspect : float
            azimuth of plane
        dip : float
            inclination of plane in direction of aspect

    Returns
    -------
    array

    Examples
    --------
        >>> import numpy as np
        >>> azimuth = np.array(range(0, 360, 45))
        >>> horizon = (azimuth * 0) + 30
        >>> rotate_horizon(azimuth, horizon, 135, 30)
        array([[3.53123432e+02, 2.88978862e+01, 6.95972227e+01, 1.35000000e+02,
                2.00402777e+02, 2.41102114e+02, 2.76876568e+02, 3.15000000e+02],
               [7.28624519e+00, 2.56589063e+01, 4.76632205e+01, 6.00000000e+01,
                4.76632205e+01, 2.56589063e+01, 7.28624519e+00, 1.42108547e-14]])

    """

    # ensure inputs are arrays
    azimuth = np.asarray(azimuth)
    horizon = np.asarray(horizon)

    # change to cartesian coordinates and rotate
    cart_coords = horiz_to_carte(azimuth, horizon)
    rot_matrix = rotate_towards(aspect, -dip)
    rot = np.dot(rot_matrix, cart_coords)

    # put back in spherical coordinates
    coords = carte_to_horiz(rot[0], rot[1], rot[2])


    # put negative horizons at 0 degrees (Assume self-shading)
    coords[1] = [x if x>=0 else 0 for x in coords[1]]

    return(coords)


def project_horizon_to_equirectangular(azimuth, horizon, r0=1, degrees=True):
    """ Project azimuth and horizon onto x,y plane using equirectangular projection


    Parameters
    ----------
        azimuth: array_like
            azimuthal direction
        horizon: array_like
            horizon angle (angle between point, origin and projection of point on x,y plane)
        r0 : array_like
            radius of points
        degrees : boolean
            Whether azimuth and horizon are input in degrees

    Examples
    --------
        import numpy as np
        >>> project_horizon_to_equirectangular(90, 0)
        (1.0, 0.0)
        >>> project_horizon_to_equirectangular(180, 45)
        (0.0, -0.5)
        >>> project_horizon_to_equirectangular(0, 90)
        (0.0, 0.0)
    """
    if degrees:
        azimuth = np.radians(azimuth)
        horizon = np.radians(horizon)

    offset = np.pi / 2
    r =  (np.pi / 2 - horizon) * r0 / (np.pi/2)

    x = np.round(np.cos(offset - azimuth) * r, 10)
    y = np.round(np.sin(offset - azimuth) * r, 10)

    return x,y


def project_horizon_top_down(azimuth, horizon, r0=1, degrees=True):
    """ Project azimuth and horizon onto x,y plane

    Parameters
    ----------
        azimuth: array_like
            azimuthal direction
        horizon: array_like
            horizon angle (angle between point, origin and projection of point on x,y plane)
        r0 : array_like
            radius of points
        degrees : boolean
            Whether azimuth and horizon are input in degrees

    Examples
    --------
        >>> project_horizon_top_down(90, 0)
        (1.0, 0.0)
        >>> project_horizon_top_down(180, 45)
        (0.0, -0.7071067812)
        >>> project_horizon_top_down(0, 90)
        (0.0, 0.0)
    """
    if degrees:
        azimuth = np.radians(azimuth)
        horizon = np.radians(horizon)

    offset = np.pi / 2

    x = np.round(np.cos(horizon) * np.cos(offset - azimuth), 10)
    y = np.round(np.cos(horizon) * np.sin(offset - azimuth) , 10)

    return x,y


def add_sky_plot(figure, *args, **kwargs):
    ax = figure.add_subplot(*args, **kwargs, projection='polar')
    ax.set_theta_direction(1)
    ax.set_theta_zero_location('N')
    ax.yaxis.set_visible(False)
    ax.set_ylim(0, 1)
    return ax


def plot_rotated_points(azimuth, horizon, aspect, dip, ax):

    rt = rotate_horizon(azimuth, horizon, aspect, dip)

    x,y = project_horizon_to_equirectangular(rt[0], rt[1])
    r = np.sqrt(x**2 + y**2)
    azimuth = np.mod(np.arctan2(x,y), 2 * np.pi)
    p = ax.plot(azimuth, r, 'r-')

    return p


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
    xp = [np.cos(np.radians(h)) * np.cos(np.radians(90 - t)) for (t, h) in zip(theta, horiz)]
    yp = [np.cos(np.radians(h)) * np.sin(np.radians(90 - t)) for (t, h) in zip(theta, horiz)]

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
    xp, yp = project_horizon_top_down(theta, horiz)

    # Draw out the horizon line (we will test for intersections later)
    xy = np.array([[x,y] for (x,y) in zip(xp, yp)])
    L  = LinearRing(xy)  # horizon line

    obscured_points = []

    # make test points halfway around the circle (
    for angle in range(0,180, increment):

        # make line across horizon
        x_test = 2 * np.cos(np.radians(90 - angle))
        y_test = 2 * np.sin(np.radians(90 - angle))
        l = LineString([[x_test, y_test], [-x_test, -y_test]])

        # get intersection with horizon
        pts = l.intersection(L)

        if pts:
            pass # intersects horizon at least once
        else:
            obscured_points.append(angle) # no intersection
            obscured_points.append( (180 + angle) % 360)

    return(np.array(obscured_points))


if __name__ == "__main__":
    import doctest
    doctest.testmod()


