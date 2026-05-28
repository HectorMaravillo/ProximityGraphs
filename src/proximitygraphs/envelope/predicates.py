"""Elementary circle predicates and planar helpers."""

import numpy as np


def slope(p, q):
    """
    Slope between two points.

    Parameters
    ----------
    p, q : (2,) array_like
        Cartesian coordinates.

    Returns
    -------
    float
        `(p_y - q_y) / (p_x - q_x)` if `p_x != q_x`, else `np.inf`.
    """
    delta_x = p[0] - q[0]
    delta_y = p[1] - q[1]
    if delta_x == 0:
        return np.inf
    else:
        return delta_y / delta_x


def is_in_circle(center, radius, point):
    """
    Membership test for a closed disk.

    Parameters
    ----------
    center : (2,) array_like
        Circle center.
    radius : float
        Circle radius (nonnegative).
    point : (2,) array_like
        Query point.

    Returns
    -------
    bool
        True if `||point - center||_2 <= radius`, else False.
    """
    return np.linalg.norm(center - point) <= radius
