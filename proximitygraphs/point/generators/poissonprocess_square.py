"""Homogeneous Poisson point process in a square."""

import numpy as np
from scipy.stats import poisson, uniform


def poissonprocess_square(cls, intensity=10, limit=1, seed=None):
    """
    Generates points according to a homogeneous Poisson point process
    in a square region.

    A 2D homogeneous Poisson point process is characterized by a constant intensity
    (lambda, denoted as `intensity` here) which represents the average number of
    points per unit area.

    The generation process involves two steps:
    1.  The number of points, `N`, to be generated in the square region is drawn
        from a Poisson distribution with mean `L = intensity * area`. The `area`
        is calculated as `(xmax - xmin) * (ymax - ymin)`, where the simulation
        window is defined by `(xmin, ymin)` to `(xmax, ymax)`. In this method,
        `xmin` and `ymin` are 0, and `xmax` and `ymax` are `limit`.
        So, `area = limit^2`.
    2.  Given `N` points, their x-coordinates are drawn independently from a
        uniform distribution U(0, `limit`), and their y-coordinates are drawn
        independently from a uniform distribution U(0, `limit`).

    This results in a set of points whose locations are random and uniformly
    distributed within the square defined by `(0,0)` and `(limit, limit)`.

    Parameters:
    ----------
    intensity : float
        The intensity (lambda) of the Poisson process, representing the average
        number of points per unit area. Must be a positive value.
    limit : float
        The side length of the square simulation window, which extends from
        (0,0) to (limit, limit). Must be a positive value.
    seed : int, optional
        A seed for the random number generator to ensure reproducibility.
        If None, the RNG is initialized without a specific seed. Defaults to None.
    """
    try:
        if intensity <= 0 or limit <= 0:
            raise ValueError("intensity and limit must be positive values")
    except ValueError as e:
        print(e)

    rng = np.random.default_rng(seed=seed)
    limits = ((0, limit), (0, limit))
    # Simulation window parameters
    xmin, xmax = limits[0]
    ymin, ymax = limits[1]
    xdelta = xmax - xmin
    ydelta = ymax - ymin
    area = xdelta * ydelta
    n_points = poisson(intensity * area).rvs(random_state=rng)
    x = xdelta * uniform.rvs(0, 1, size=((n_points, 1)), random_state=rng) + xmin
    y = ydelta * uniform.rvs(0, 1, size=((n_points, 1)), random_state=rng) + ymin
    points = np.hstack((x, y))
    return cls(points, seed=rng.integers(low=0, high=2**32 - 1))
