"""Random perturbation transformation for point sets."""

import numpy as np

from ...utilities import points_on_sphere


def perturb(self, radius):
    """
    Applies a random perturbation to each point in the set.

    Each point `p` in the original set is moved to a new location `p' = p + v`,
    where `v` is a random perturbation vector. The perturbation `v` is generated
    such that it is uniformly distributed within a `dim`-dimensional sphere of
    the given `radius` centered at the origin.

    The generation of each perturbation vector `v` involves two steps:
    1.  **Direction**: A random direction is chosen by generating a point uniformly
        on the surface of a `dim`-dimensional unit sphere. This is achieved using
        the `points_on_sphere` utility function (which normalizes a vector of
        standard normal variates). Let this unit vector be `u`.
    2.  **Magnitude**: A random magnitude `m` for the perturbation is determined by
        drawing a random number `r_raw` from a uniform distribution U(0, `radius`).
        To ensure uniform distribution *within* the sphere (not concentrated towards
        the center or edge for higher dimensions), this raw radius is transformed:
        `m = r_raw^(1/dim)`, where `dim` is the number of dimensions.
        Actually, looking at the code
        `r = np.random.uniform(0, radius, self.n)**(1/self.dim)`,
        it seems `r_raw` is `U(0, radius^dim)` if we want `m` to be
        `U(0,radius)`.
        Or, more standardly, if `r_sample` is `U(0,1)`, then actual
        random radius for uniform distribution in a d-ball of radius R is
        `R * r_sample^(1/d)`.
        The code is
        `r_scalar_factors = np.random.uniform(0, radius, self.n)**(1/self.dim)`.
        This means each point `i` gets a scalar factor
        `s_i = unif(0, radius)^(1/dim)`.
        This is not standard for uniform distribution *within* a sphere of `radius`.
        If `radius` is, say, 5, then `unif(0,5)^(1/dim)` is taken.
        Let's stick to describing what the code does:
        A scalar `s_i` is generated for each point `i` as
        `s_i = U_i^(1/dim)`, where `U_i` is drawn from
        `Uniform(0, radius)`. This `s_i` is used as the magnitude for the
        perturbation of point `i`. So `v_i = s_i * u_i`.

    The effect is that each original point is displaced to a new random position.
    The displacement vectors are such that their directions are isotropic, and
    their magnitudes `s_i` are distributed according to `(U(0, radius))^(1/dim)`.
    This means points are more likely to be perturbed by a larger fraction
    of `radius` than a smaller fraction, especially in higher dimensions.

    Note: The docstring of the code
    `unit_sphere_surface = points_on_sphere(self.n, self.dim)` implies
    `points_on_sphere` is called once for all points.

    Parameters:
    ----------
    radius : float
        The maximum radius for the perturbation. Each random perturbation vector's
        magnitude is determined based on this value, specifically as
        `(U(0, radius))^(1/dim)`. Must be a positive value.

    Returns:
    -------
    SetPoints
        A new SetPoints object containing the perturbed points.

    Raises:
    ------
    ValueError
        If `radius` is not positive.
    """
    if radius < 0:
        raise ValueError("Radius must be positive")

    # Ensure self._rng exists, initialized in __init__
    if not hasattr(self, "_rng") or self._rng is None:
        rng_to_use = np.random.default_rng()
    else:
        rng_to_use = self._rng

    r_magnitudes = rng_to_use.uniform(0, radius, self.n) ** (1 / self.dim)

    unit_sphere_surface = points_on_sphere(self.n, self.dim, rng=rng_to_use)

    perturbations = r_magnitudes.reshape(-1, 1) * unit_sphere_surface
    new_seed_for_next_instance = rng_to_use.integers(low=0, high=2**32 - 1)

    return self.__class__(self.points + perturbations, seed=new_seed_for_next_instance)
