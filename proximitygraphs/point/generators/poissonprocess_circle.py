"""Homogeneous Poisson point process on a circle."""

import numpy as np


def poissonprocess_circle(cls, intensity=10, radius=1, seed=None):
    """
    Generates points according to a homogeneous Poisson point process on
    the circumference of a circle.

    This method simulates points positioned on the perimeter of a circle
    of a given `radius`.
    The process is homogeneous, meaning the intensity of points is uniform
    along the circumference.

    The generation process involves two main steps:
    1.  The number of points, `N`, to be placed on the circumference is drawn
        from a Poisson distribution. The mean of this distribution is
        `L = intensity * length`, where `length` is the circumference of the
        circle (2 * pi * `radius`). The `intensity` parameter here represents the
        average number of points per unit length along the circumference.
    2.  Given `N` points, their angular positions (theta) are drawn independently
        from a uniform distribution U(0, 2*pi). These angles are then converted
        to Cartesian coordinates (x, y) using the standard transformation:
        x = `radius` * cos(theta)
        y = `radius` * sin(theta)

    This results in a set of points randomly distributed along the circumference
    of the circle.

    Parameters:
    ----------
    intensity : float
        The intensity (lambda) of the Poisson process, representing the average
        number of points per unit length along the circumference.
    radius : float
        The radius of the circle on whose circumference the points will be
        generated.
        Must be a positive value.
    seed : int, optional
        A seed for the random number generator to ensure reproducibility.
        If None, the RNG is initialized without a specific seed. Defaults to None.
    """
    rng = np.random.default_rng(seed=seed)
    length = 2 * np.pi * radius
    n_points = rng.poisson(intensity * length)
    theta = 2 * np.pi * rng.uniform(0, 1, n_points)
    x = radius * np.cos(theta)
    y = radius * np.sin(theta)
    points = np.stack((x, y), axis=1)
    return cls(points, seed=rng.integers(low=0, high=2**32 - 1))
