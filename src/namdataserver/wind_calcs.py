# This code accessed from https://github.com/blaylockbk/Ute_WRF/blob/master/functions/wind_calcs.py
# on August 8 2022 -rehosted by permission of author 
# Brian Blaylock
# 7 December 2015


# Various Wind Calculations
#   Change wind speed and direction to U and V components
#   Change U and V components to direction
#   Change U and V components to speed
#   Calculate the angle between two vecors [u1,v1] and [u2,v2]


import numpy as np

def wind_spddir_to_uv(wspd,wdir):
    """Calculate the u and v wind components from wind speed and direction.

    :param wspd: wind speed
    :type wspd: float
    :param wdir: wind direction
    :type wdir: float
    :return u: west/east direction (wind from the west is positive, from the east is negative
    :rtype u: float
    :return v: south/noth direction (wind from the south is positive, from the north is negative
    :rtype v: float



    |br|
    """

    rad = 4.0*np.arctan(1)/180.
    u = -wspd*np.sin(rad*wdir)
    v = -wspd*np.cos(rad*wdir)

    return u,v

def wind_uv_to_dir(U,V):
    """
    Calculates the wind direction from the u and v component of wind.
    Takes into account the wind direction coordinates is different than the
    trig unit circle coordinate. If the wind directin is 360 then returns zero
    (by %360)

    :param u: west/east direction (wind from the west is positive, from the east is negative
    :type u: float
    :param v: south/noth direction (wind from the south is positive, from the north is negative
    :type v: float
    :return WDIR: Direction of Wind
    :rtype: float



    |br|

    """
    WDIR= (270-np.rad2deg(np.arctan2(V,U)))%360
    return WDIR

def wind_uv_to_spd(U,V):
    """
    Calculates the wind speed from the u and v wind components

    :param u: west/east direction (wind from the west is positive, from the east is negative
    :type u: float
    :param v: south/noth direction (wind from the south is positive, from the north is negative
    :type v: float
    :return WSPD: Wind Speed
    :rtype: float



    |br|

    """
    WSPD = np.sqrt(np.square(U)+np.square(V))
    return WSPD


# Below is used for calculing the angle between two wind vectors
def unit_vector(vector):
    """ Returns the unit vector of the vector.



    |br|

    """
    return vector / np.linalg.norm(vector)

def angle_between(v1, v2):
    """
    Calcualates the angle between two wind vecotrs. Utilizes the cos equation:
                cos(theta) = (u dot v)/(magnitude(u) dot magnitude(v))

    Input:

    ::

      v1 = vector 1. A numpy array, list, or tuple with
            u in the first index and v in the second --> vector1 = [u1,v1]
      v2 = vector 2. A numpy array, list, or tuple with
             u in the first index and v in the second --> vector2 = [u2,v2]

    Output:
    Returns the angle in radians between vectors 'v1' and 'v2'

    ::

      >>> angle_between((1, 0, 0), (0, 1, 0))
          1.5707963267948966
      >>> angle_between((1, 0, 0), (1, 0, 0))
          0.0
      >>> angle_between((1, 0, 0), (-1, 0, 0))
          3.141592653589793

    |br|

    .. |br| raw:: html

        <br>

    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    angle = np.arccos(np.dot(v1_u, v2_u))
    if np.isnan(angle):
        if (v1_u == v2_u).all():
            return np.rad2deg(0.0)
        else:
            return np.rad2deg(np.pi)
    return np.rad2deg(angle)
