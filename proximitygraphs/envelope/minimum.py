"""Minimum enclosing circle routines.

The minimum enclosing circle routine follows the standard randomized
incremental idea: maintain a small boundary set of points that must lie on the
enclosing circle, then recurse until the boundary determines the disk.

References
----------
De Berg, M., Cheong, O., Van Kreveld, M., & Overmars, M. (2008).
Computational Geometry: Algorithms and Applications. Springer.
"""

import numpy as np

from .predicates import is_in_circle


def trivial_circle(points):
    """
    Minimum Enclosing Circle for at most three points.

    Parameters
    ----------
    points : sequence of (2,) array_like
        Zero to three points.

    Returns
    -------
    center : (2,) ndarray
        Circle center.
    radius : float
        Circle radius.

    Notes
    -----
    Exact formulas:
    - 0 points  -> center = [0, 0], radius = 0
    - 1 point   -> center = p, radius = 0
    - 2 points  -> midpoint and half-distance
    - 3 points  -> `circle_through_three_points`
    """
    from .constructors import circle_through_three_points, circle_through_two_points

    if len(points) == 0:
        return np.array([0, 0]), 0
    elif len(points) == 1:
        return np.array(points[0]), 0
    elif len(points) == 2:
        center, radius = circle_through_two_points(np.array(points))
        return center, radius
    elif len(points) == 3:
        center, radius = circle_through_three_points(np.array(points))
        return center, radius


def smallest_circle_helper(points, boundary):
    """
    Recursive Minimum Enclosing Circle helper with boundary set.

    Parameters
    ----------
    points : (m, 2) ndarray
        Remaining points not yet enforced to lie inside the circle.
    boundary : list of (2,) array_like
        Points that must lie on the boundary (size 0..3).

    Returns
    -------
    center : (2,) ndarray
        Current Minimum Enclosing Circle center consistent with `boundary`.
    radius : float
        Current Minimum Enclosing Circle radius.
    """
    if points.shape[0] == 0 or len(boundary) == 3:
        return trivial_circle(boundary)
    else:
        p = points[-1]
        center, radius = smallest_circle_helper(points[:-1], boundary.copy())
        if is_in_circle(center, radius, p):
            return center, radius
        boundary.append(list(p))
        center, radius = smallest_circle_helper(points[:-1], boundary.copy())
    return center, radius


def smallest_circle(points):
    """
    Minimum enclosing circle of a planar point cloud.

    Parameters
    ----------
    points : (n, 2) array_like
        Input points. Duplicates allowed. `n >= 0`.

    Returns
    -------
    center : (2,) ndarray
        Minimum Enclosing Circle center.
    radius : float
        Minimum Enclosing Circle radius.
    """
    points_copy = points.copy()
    np.random.default_rng().shuffle(points_copy)
    center, radius = smallest_circle_helper(points_copy, [])
    return center, radius
