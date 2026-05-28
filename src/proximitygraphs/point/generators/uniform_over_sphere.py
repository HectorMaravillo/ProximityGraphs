"""Uniform sampling on the unit circle."""

import numpy as np

from ...utilities import points_on_sphere


def uniform_over_sphere(cls, n=10, seed=None):
    """
    Generate a random uniform sample of points on the unit circle S^1 subset R^2.

    Mechanism
    ---------
    Draw Z ~ N(0, I2), then project onto the circle:
        X = Z / ||Z||2
    This produces a rotationally-invariant (uniform) distribution on S^1.

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
    points = points_on_sphere(n, 2, rng=rng)
    return cls(points)
