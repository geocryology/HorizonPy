import numpy as np
from scipy.interpolate import interp1d
from itertools import izip


def SVF_discretized(azi, hor, plane_az, plane_dip, delta_phi, interpolation='linear'):
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
    # Ensure correct data structure and sort
    azi = np.array(azi) if type(azi) != np.ndarray and hasattr(azi, '__len__') else azi
    hor = np.array(hor) if type(hor) != np.ndarray and hasattr(hor, '__len__') else hor
    azi = azi[np.argsort(azi)]
    hor = hor[np.argsort(azi)] # sorting to order by azimuth
    
    # Calculate adjusted horizon angles relative to (possibly) non-horizontal surface
    hor_rot = hor + angl_rotate(plane_dip, (azi - plane_az))
    
    # Create spline equation to obtain hor(az) for any azimuth
    # add endpoints on either side of sequence so interpolation is good 
    x = np.concatenate((azi[-2:]-360, azi, azi[:2]+360)) 
    y = np.concatenate((hor_rot[-2:], hor_rot, hor_rot[:2]))

    f_hor = interp1d(x, y, kind = interpolation)
    
    # Measure rotated horizon at evenly spaced interval using spline
    phi = np.array(range(0, 360, delta_phi))
    theta_h = f_hor(phi)
    
    cos2theta = np.power(np.cos(theta_h * np.pi / 180), 2)
    
    # To deal with overhanging terrain, take negative cos2() if the horizon
    # is greater than 90. This might be wrong... But otherwise overhanging 
    # terrain doesn't increases the skyview factor
    S = [y if x <= 90 else -y for (x, y) in izip(theta_h, cos2theta)] 

    F_sky = (delta_phi / 360.) * np.sum(S)
    return(F_sky)


    
def angl_rotate(dip, rot):
    """
    Gives the angle relative to horizontal of a vector rotated from the 
    direction of steepest decent
    """
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
    rotated_dip = (np.arcsin(np.sin(dip * np.pi / 180) * np.cos(rot * np.pi / 180))) 
    rotated_dip *= (180 / np.pi)
    rotated_dip = np.round(rotated_dip, 5)
    
    return(rotated_dip)    
    