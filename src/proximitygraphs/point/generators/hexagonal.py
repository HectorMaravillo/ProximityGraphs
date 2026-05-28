"""Hexagonal lattice point generation."""

import numpy as np


def hexagonal(cls, n_x=3, n_y=3):
    """
    Generates points forming a hexagonal lattice in a 2D plane.

    A hexagonal lattice can be represented as the union of two interleaved
    rectangular (or oblique) grids. This implementation constructs it as such.
    Points in a hexagonal grid are centers of hexagons in a tessellation.

    The method first generates a base grid (`grid_1`). The x-coordinates in
    this grid are spaced by alternating increments (e.g., 1, 2, 1, 2,...),
    and y-coordinates are spaced by `sqrt(3)` (or `2*sqrt(3)`
    depending on interpretation).
    A second grid (`grid_2`) is then generated. Its x-coordinates are also
    spaced by alternating increments but offset from `grid_1` (e.g., by -0.5
    relative to a scaled version of `grid_1`'s x-pattern). The y-coordinates
    of `grid_2` are also spaced by `sqrt(3)` but are offset vertically from
    `grid_1`'s y-coordinates by `0.5 * sqrt(3)`.

    The combination of these two grids results in the characteristic hexagonal
    pattern where each point has 6 equidistant neighbors (assuming appropriate
    scaling).

    Note: This implementation is for 2D hexagonal grids only.
    The `n_x` and `n_y` parameters control the extent of the grid.

    Parameters:
    ----------
    n_x : int
        Determines the extent of the hexagonal grid along an axis roughly aligned
        with the x-direction. It influences the number of columns.
    n_y : int
        Determines the extent of the hexagonal grid along an axis roughly aligned
        with the y-direction. It influences the number of rows.
    """
    try:
        if n_x <= 0 or n_y <= 0:
            raise ValueError("n_x and n_y must be positive integers")
    except ValueError as e:
        print(e)

    x = np.cumsum(np.array([1, 2] * n_x))
    x = np.insert(x, 0, 0)
    y = np.cumsum(np.array([np.sqrt(3)] * 2 * n_y))
    y = np.insert(y, 0, 0)
    xv, yv = np.meshgrid(x, y)
    grid_1 = np.array(list(zip(xv.flat, yv.flat, strict=False)))
    x = np.cumsum(np.array([2, 1] * n_x))
    x = np.insert(x, 0, 0) - 0.5
    y = np.cumsum(np.array([np.sqrt(3)] * 2 * n_y))
    y = np.insert(y, 0, 0)
    y = y + 0.5 * np.sqrt(3)
    xv, yv = np.meshgrid(x, y)
    grid_2 = np.array(list(zip(xv.flat, yv.flat, strict=False)))
    points = np.concatenate((grid_1, grid_2))
    return cls(points)
