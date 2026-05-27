"""Inhomogeneous Poisson point process by thinning."""

import numpy as np
from scipy.optimize import minimize


def poissonprocess_inhomogeneus(
    cls,
    fun_lambda=lambda x, y: x + y,
    n_sim=1,  # This parameter is unused
    limit=1,
    seed=None,
):
    """
    Generates points according to an inhomogeneous Poisson point process
    in a square region using thinning.

    An inhomogeneous (or nonhomogeneous) Poisson point process is
    characterized by an intensity function `fun_lambda(x,y)` that varies
    spatially. The value of
    `fun_lambda(x,y)` at a point (x,y) dictates the likelihood of finding a point
    in the infinitesimal area around (x,y).

    This method uses the thinning algorithm (also known as
    acceptance-rejection sampling):
    1.  **Find Maximum Intensity (`lambda_max`)**: The maximum value of the
        intensity function `fun_lambda(x,y)` within the simulation window
        `(0, limit) x (0, limit)`
        is determined. This is done by numerically minimizing `-fun_lambda(x,y)`
        using `scipy.optimize.minimize`.
    2.  **Generate Homogeneous Proposal Points**: A set of proposal points is
        generated from a homogeneous Poisson point process with constant
        intensity `lambda_max` over the square simulation window (area =
        `limit`*`limit`). The number of these proposal points, `N_prop`,
        is drawn from Poisson(`lambda_max` * area).
        Their coordinates are uniformly distributed within the square.
    3.  **Thinning**: Each proposal point `(x_i, y_i)` is "kept" or "thinned"
        (discarded) based on a spatially dependent probability. The probability of
        keeping a point at `(x_i, y_i)` is
        `p(x_i, y_i) = fun_lambda(x_i, y_i) / lambda_max`.
        This is achieved by generating a random number `u_i` from U(0,1) for each
        proposal point and keeping the point if `u_i < p(x_i, y_i)`.

    The resulting set of retained points follows the inhomogeneous Poisson process
    defined by `fun_lambda(x,y)`.

    Parameters:
    ----------
    fun_lambda : callable
        A function that takes two arguments (x, y coordinates) and returns the
        intensity of the Poisson process at that point.
        Example: `lambda x, y: x + y`
    n_sim : int
        This parameter appears in the original signature but is not used in the
        current implementation. (Consider for future review/deprecation).
    limit : float
        The side length of the square simulation window, which extends from
        (0,0) to (limit, limit). The process is simulated within this area.
    seed : int, optional
        A seed for the random number generator to ensure reproducibility.
        If None, the RNG is initialized without a specific seed. Defaults to None.
    """
    rng = np.random.default_rng(seed=seed)
    limits = ((0, limit), (0, limit))
    # fun_lambda = lambda x,y: np.cos(2*x)+np.cos(2*y)
    xmin, xmax = limits[0]
    ymin, ymax = limits[1]
    xdelta = xmax - xmin
    ydelta = ymax - ymin
    area = xdelta * ydelta

    # Find maximum lambda
    def fun_neg(x):
        return -fun_lambda(x[0], x[1])

    xy0 = [(xmin + xmax) / 2, (ymin + ymax) / 2]
    results_opt = minimize(fun_neg, xy0, bounds=((xmin, xmax), (ymin, ymax)))
    lambda_neg_min = results_opt.fun
    lambda_max = -lambda_neg_min

    # define thinning probability function
    def fun_p(x, y):
        return fun_lambda(x, y) / lambda_max

    # Simulate a Poisson point process
    # Corrected n_poins to n_points
    n_points = rng.poisson(area * lambda_max)
    x = rng.uniform(0, xdelta, size=((n_points, 1))) + xmin
    y = rng.uniform(0, ydelta, size=((n_points, 1))) + ymin
    # calculate spatially-dependent thinning probabilities
    p = fun_p(x, y)
    # Generate Bernoulli variables (ie coin flips) for thinning
    retained = rng.uniform(0, 1, size=((n_points, 1))) < p
    # x/y locations of retained points
    x_retained = x[retained]
    y_retained = y[retained]
    points = np.stack((x_retained, y_retained), axis=1)
    return cls(points, seed=rng.integers(low=0, high=2**32 - 1))
