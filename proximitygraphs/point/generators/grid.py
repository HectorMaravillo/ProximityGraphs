"""Regular grid point generation."""

import numpy as np


def grid(cls, shape=(3, 3)):
    """
    Generates a regular 2D grid of points.

    The points form a 2D grid. The `shape` parameter is a tuple (n_x, n_y)
    defining the number of steps along each axis.

    Coordinates are integers on each axis. This implementation uses:
        x in {0, 1, ..., n_x}
        y in {0, 1, ..., n_y}
    via numpy.arange(0, n_i + 1), then builds all combinations with meshgrid.

    Parameters
    ----------
    shape : tuple of int
        A tuple (n_x, n_y). Only 2D grids are supported.

    Returns
    -------
    cls
        Instance with points of shape ((n_x+1)*(n_y+1), 2).
    """
    if not isinstance(shape, tuple):
        raise ValueError("shape must be a tuple")
    if len(shape) != 2:
        raise ValueError("shape must be a tuple of length 2: (n_x, n_y)")
    nx, ny = shape
    if not (isinstance(nx, int) and isinstance(ny, int)) or nx <= 0 or ny <= 0:
        raise ValueError("shape entries must be positive integers")

    axes = [np.arange(0, nx), np.arange(0, ny)]
    mesh = np.meshgrid(*axes, indexing="ij")
    points = np.column_stack([m.ravel() for m in mesh])
    return cls(points)
