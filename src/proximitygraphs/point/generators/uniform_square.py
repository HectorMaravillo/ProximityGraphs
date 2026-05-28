"""Uniform sampling in the unit square."""

import numpy as np


def uniform_square(cls, n=10, seed=None):
    """
    Generate a random uniform sample of points in the unit square [0,1]^2.

    Mechanism
    ---------
    Let X = (X1, X2) in R^2. Sample coordinates independently:
        X1 ~ U(0,1),  X2 ~ U(0,1)  (i.i.d.)
    Then X is uniform over the unit square (constant density on [0,1]^2).

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
    points = rng.random((n, 2))
    return cls(points)
