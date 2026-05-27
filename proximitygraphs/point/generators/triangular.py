"""Triangular lattice point generation."""

import numpy as np


def triangular(cls, n_x=3, n_y=3):
    """
    Generates points forming a triangular lattice in a 2D plane.

    A triangular lattice can be seen as the centers of a triangular tessellation
    of the plane. It is constructed by combining two offset grids:

    1.  The first grid (`grid_1`) has points `(i, j * sqrt(3))` where `i` ranges
        from `0` to `n_x` and `j` ranges over multiples for `n_y` rows.
        Specifically, x-coordinates are `0, 1, 2, ..., n_x`.
        Y-coordinates are `0, sqrt(3), 2*sqrt(3), ...`.

    2.  The second grid (`grid_2`) is offset from the first. Its points are
        `(i + 0.5, (j + 0.5) * sqrt(3))`.
        Specifically, x-coordinates are `0.5, 1.5, 2.5, ...`.
        Y-coordinates are `0.5*sqrt(3), 1.5*sqrt(3), ...`.

    The combination of these two grids forms a triangular lattice. Each point in
    this lattice has 6 equidistant neighbors, forming equilateral triangles.
    The term `sqrt(3)` arises from the height of an equilateral triangle with
    side length 1 (if x-spacing is 1 unit between points on the same horizontal line
    of a sub-grid).

    Note: This implementation is for 2D triangular grids only.
    The `n_x` and `n_y` parameters control the extent of the grid.
    The existing docstring has a typo: "surface of the hexagon" should be
    related to triangles.

    Parameters:
    ----------
    n_x : int
        Determines the extent of the triangular grid along the x-direction.
        It influences the number of points in horizontal rows of the sub-grids.
    n_y : int
        Determines the extent of the triangular grid along the y-direction.
        It influences the number of rows in the sub-grids.
    """
    try:
        if n_x <= 0 or n_y <= 0:
            raise ValueError("n_x and n_y must be positive integers")
    except ValueError as e:
        print(e)

    x = np.arange(0, n_x + 1)
    y = np.arange(0, np.sqrt(3) * np.floor(n_y / 2) + 1, np.sqrt(3))
    xv, yv = np.meshgrid(x, y)
    grid_1 = np.array(list(zip(xv.flat, yv.flat, strict=False)))
    x = x + 0.5
    y = np.arange(np.sqrt(3) / 2, np.sqrt(3) * np.ceil(n_y / 2), np.sqrt(3))
    xv, yv = np.meshgrid(x, y)
    grid_2 = np.array(list(zip(xv.flat, yv.flat, strict=False)))
    points = np.concatenate((grid_1, grid_2))
    return cls(points)
