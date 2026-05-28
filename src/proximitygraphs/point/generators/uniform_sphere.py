"""Uniform sampling in the unit disk."""

import numpy as np

from ...utilities import points_on_sphere


def uniform_sphere(cls, n=10, seed=None):
    """
    Generate a random uniform sample of points in the unit disk B^2 subset R^2.

    Mechanism
    ---------
    1) Sample a direction uniformly on S^1 via U = Z / ||Z||2, with Z ~ N(0, I2).
    2) Sample radius with area-correct scaling: if V ~ U(0,1), set R = sqrt(V).
    This gives P(R <= r) = r^2, which matches uniform area in the disk.
    3) Set X = R * U.

    Parameters
    ----------
    n : int
        Number of points.
    seed : int or None
        RNG seed. If None, uses entropy from the OS (non-deterministic).

    Returns
    -------
    cls
        Instance with points of shape (n, 2).
    """
    if not isinstance(n, int) or n <= 0:
        raise ValueError("n must be a positive integer")

    rng = np.random.default_rng(seed)

    radius = np.sqrt(rng.random((n, 1)))
    direction = points_on_sphere(n, 2, rng=rng)  # points on S^1
    points = radius * direction
    return cls(points)
