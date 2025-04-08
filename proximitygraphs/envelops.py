import numpy as np
from itertools import combinations


def circle_centroid(setpoints):
    centroid = setpoints.centroid
    radius = np.linalg.norm(centroid-setpoints.points, axis=1).max()
    return centroid, radius


def circle_smallest(setpoints):
    return smallest_circle(setpoints.points)


###################
# Smallest circle
###################

def slope(p, q):
    # Returns the slope between two points
    delta_x = p[0]-q[0]
    delta_y = p[1]-q[1]
    if delta_x == 0:
        return np.inf
    else:
        return delta_y / delta_x


def is_in_circle(center, radius, point):
    # Check if a point is inside a circle given by a center and a radius
    return np.linalg.norm(center-point) <= radius


def circle_through_two_points(points):
    # Find the center and radius of a circle that passes through two points
    middle_point = (points[0]+points[1])/2
    radius = np.linalg.norm(middle_point-points[0])
    return middle_point, radius


def circle_through_three_points(points):
    # Calculate the slopes of the three sides
    slope_1_2 = slope(points[0], points[1])
    slope_1_3 = slope(points[0], points[2])
    # Returns the circle that covers the three points if they are collinear
    if slope_1_2 == slope_1_3:
        max_dist = 0
        for p, q in combinations(points, 2):
            dist = np.linalg.norm(p-q)
            if dist > max_dist:
                max_dist = dist
                max_p = p
                max_q = q
        return circle_through_two_points(np.vstack((max_p, max_q)))
    # Returns the circle through the three points if they are collinear
    else:
        # Calculate the midpoint of two sides
        midpoint_12 = (points[0]+points[1])/2
        midpoint_13 = (points[0]+points[2])/2
        # Calculate the slope of the perpendicular of two sides
        slope_perpendicular_12 = -1/slope_1_2
        slope_perpendicular_13 = -1/slope_1_3
        # Finding the point of intersection of two lines
        matrix_a = np.array([[-slope_perpendicular_12, 1],
                             [-slope_perpendicular_13, 1]])
        b = np.array([midpoint_12[1]-slope_perpendicular_12*midpoint_12[0],
                      midpoint_13[1]-slope_perpendicular_13*midpoint_13[0]])
        center = np.linalg.solve(matrix_a, b)
        radius = np.linalg.norm(center-points[0])
        return center, radius


def trivial_circle(points):
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
    points_copy = points.copy()
    np.random.shuffle(points_copy)
    center, radius = smallest_circle_helper(points_copy, [])
    return center, radius
