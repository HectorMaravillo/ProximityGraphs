"""Sphere point-picking utilities.

This module generates points uniformly on the unit sphere by normalizing
independent Gaussian vectors. The method relies on rotational invariance of the
multivariate normal distribution, producing directions that are uniform on the
sphere surface.

References
----------
Weisstein, E. W. Sphere Point Picking. MathWorld.
https://mathworld.wolfram.com/SpherePointPicking.html
"""

import numpy as np


def points_on_sphere(n, dims=2, seed=None, rng=None):
    """
    Generate n points uniformly on the surface of the unit (dims-1)-sphere.

    References
    ----------
    https://mathworld.wolfram.com/SpherePointPicking.html
    https://math.stackexchange.com/questions/444700/uniform-distribution-on-the-surface-of-unit-sphere

    Mechanism (Gaussian normalization)
    -------------------------------
    1) Sample X in R^dims with i.i.d. standard normal entries.
    2) Normalize each row by its Euclidean norm: Y = X / ||X||.
       By rotational invariance of the Gaussian, Y is uniform on the sphere.

    Parameters
    ----------
    n : int
        Number of points.
    dims : int
        Dimension of the ambient space. For your module, keep this fixed to 2.
    seed : int or None
        RNG seed used only if rng is None. If None, uses OS entropy (non-deterministic).
    rng : numpy.random.Generator or None
        If provided, used as the random number generator (seed is ignored).

    Returns
    -------
    Y : ndarray, shape (n, dims)
        Points on the unit sphere (each row has norm 1).
    """
    if not isinstance(n, int) or n <= 0:
        raise ValueError("n must be a positive integer")
    if dims != 2:
        raise ValueError("dims must be 2 (this module is restricted to 2D)")

    if rng is None:
        rng = np.random.default_rng(seed)

    # Draw from N(0, I_dims)
    X = rng.normal(size=(n, dims))

    X_norm = np.linalg.norm(X, axis=1, keepdims=True)

    # Normalize rows if ||X||=0
    zero = (X_norm == 0.0).ravel()

    while np.any(zero):
        X[zero] = rng.normal(size=(zero.sum(), dims))
        X_norm[zero] = np.linalg.norm(X[zero], axis=1, keepdims=True)
        zero = (X_norm == 0.0).ravel()

    Y = X / X_norm
    return Y
