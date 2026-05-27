"""Circle constructors for point containers and small boundary sets."""

from itertools import combinations

import numpy as np

from .minimum import smallest_circle
from .predicates import slope


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
