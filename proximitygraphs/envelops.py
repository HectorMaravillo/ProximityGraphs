from itertools import combinations

import numpy as np


def circle_centroid(setpoints):
    """
    Circle centered at the centroid with maximal sample radius.

    Parameters
    ----------
    setpoints : object
        Any object exposing:
        - `centroid` : (2,) array_like
            The arithmetic centroid of the point set.
        - `points` : (n, 2) array_like of float
            The planar coordinates.

    Returns
    -------
    centroid : (2,) ndarray
        Center located at the given centroid.
    radius : float
        Max Euclidean distance from `centroid` to `setpoints.points`.
    """
    centroid = setpoints.centroid
    radius = np.linalg.norm(centroid - setpoints.points, axis=1).max()
    return centroid, radius


def circle_smallest(setpoints):
    """
    Minimum enclosing circle of a point container.

    Parameters
    ----------
    setpoints : object
        Any object exposing `points : (n, 2) array_like`.

    Returns
    -------
    center : (2,) ndarray
        Optimal circle center.
    radius : float
        Optimal radius.
    """
    return smallest_circle(setpoints.points)


###################
# Smallest circle
###################


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


def circle_through_two_points(points):
    """
    Unique circle through two points.

    Parameters
    ----------
    points : (2, 2) array_like
        Two distinct points.

    Returns
    -------
    center : (2,) ndarray
        Midpoint of the segment.
    radius : float
        Half the inter-point distance.
    """
    middle_point = (points[0] + points[1]) / 2
    radius = np.linalg.norm(middle_point - points[0])
    return middle_point, radius


def circle_through_three_points(points):
    """
    Circumcircle of three points, or diameter circle if collinear.

    Parameters
    ----------
    points : (3, 2) array_like
        Three points.

    Returns
    -------
    center : (2,) ndarray
        Circumcenter if non-collinear, else midpoint of the farthest pair.
    radius : float
        Circumradius, or half of the maximal pairwise distance if collinear.
    """
    slope_1_2 = slope(points[0], points[1])
    slope_1_3 = slope(points[0], points[2])
    # Returns the circle that covers the three points if they are collinear
    if slope_1_2 == slope_1_3:
        max_dist = 0
        for p, q in combinations(points, 2):
            dist = np.linalg.norm(p - q)
            if dist > max_dist:
                max_dist = dist
                max_p = p
                max_q = q
        return circle_through_two_points(np.vstack((max_p, max_q)))
    # Returns the circle through the three points if they are collinear
    else:
        # Calculate the midpoint of two sides
        midpoint_12 = (points[0] + points[1]) / 2
        midpoint_13 = (points[0] + points[2]) / 2
        # Calculate the slope of the perpendicular of two sides
        slope_perpendicular_12 = -1 / slope_1_2
        slope_perpendicular_13 = -1 / slope_1_3
        # Finding the point of intersection of two lines
        matrix_a = np.array(
            [[-slope_perpendicular_12, 1], [-slope_perpendicular_13, 1]]
        )
        b = np.array(
            [
                midpoint_12[1] - slope_perpendicular_12 * midpoint_12[0],
                midpoint_13[1] - slope_perpendicular_13 * midpoint_13[0],
            ]
        )
        center = np.linalg.solve(matrix_a, b)
        radius = np.linalg.norm(center - points[0])
        return center, radius


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
    np.random.shuffle(points_copy)
    center, radius = smallest_circle_helper(points_copy, [])
    return center, radius
