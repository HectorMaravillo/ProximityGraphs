"""Bivariate normal point sampling."""

import numpy as np


def normal_dist(cls, n=10, seed=None):
    """
    Generate a random sample of points from the bivariate standard normal N(0, I2).

    Mechanism
    ---------
    Draw X in R^2 with mean vector 0 and covariance matrix I2.
    Components are independent with unit variance.

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
    mean = np.zeros(2)
    cov = np.eye(2)
    points = rng.multivariate_normal(mean, cov, n)
    return cls(points)
