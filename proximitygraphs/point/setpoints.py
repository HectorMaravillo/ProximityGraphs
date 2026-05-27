"""Point-set generation, transformation, and drawing.

This module defines ``SetPoints``, the point-cloud container used by the graph
constructors. It includes deterministic grids and lattices, random samples in
squares and disks, homogeneous and inhomogeneous Poisson point processes, and
cluster processes with Matern-like and Thomas-like daughter distributions.

The class also provides affine transformations and lightweight plotting so the
same object can be used for data generation, graph construction, and exploratory
visualization.

References
----------
Harris, C. R., Millman, K. J., van der Walt, S. J., et al. (2020). Array
programming with NumPy. Nature, 585, 357-362.

Virtanen, P., Gommers, R., Oliphant, T. E., et al. (2020). SciPy 1.0:
Fundamental algorithms for scientific computing in Python. Nature Methods, 17,
261-272.

https://hpaulkeeler.com/ para point process
"""

import numpy as np

from .drawing import draw
from .generators import (
    cluster_square,
    grid,
    hexagonal,
    normal_dist,
    poissonprocess_circle,
    poissonprocess_inhomogeneus,
    poissonprocess_square,
    triangular,
    uniform_over_sphere,
    uniform_sphere,
    uniform_square,
)
from .gis import from_geopandas
from .transformations import (
    _affin_transformation,
    perturb,
    rotation,
    scaling,
    traslation,
)


class SetPoints:
    """
    Represent an ordered collection of points in the plane.

    Attributes:
        n (int): The number of points in the collection.
        points (numpy.ndarray): An 2-dimensional numpy array the points.
    """

    # ATTRIBUTES

    @property
    def n(self):
        return self.__n

    @property
    def dim(self):
        return self.__dim

    @property
    def points(self):
        return self.__points

    @property
    def pos(self):
        return dict(enumerate(self.__points))

    @property
    def centroid(self):
        return np.mean(self.__points, axis=0)

    # CONSTRUCTORS

    def __init__(self, points, seed=None):
        """
        Base constructor for SetPoints.
        attributes:
        ----------
        points : numpy.ndarray
            A 2D numpy array of shape (n, dim) where n is the number of points
            and dim is the dimension of each point.
        seed : int, optional
            A seed for the random number generator to ensure reproducibility.
            If None, a default random generator is used.
        Raises:
        ------
        TypeError: If points is not a numpy.ndarray.


        returns  a SetPoints object containing the points.
        """

        if not isinstance(points, np.ndarray):
            raise TypeError("Input 'points' must be a numpy.ndarray.")
        self.__points = points
        self.__n, self.__dim = np.shape(points)
        if seed is None:
            self._rng = np.random.default_rng()
        else:
            self._rng = np.random.default_rng(seed)

    def __add__(self, other):
        new_points = np.concatenate((self.points, other.points), axis=0)
        return SetPoints(new_points)

    def copy(self):
        return SetPoints(self.points)

    uniform_square = classmethod(uniform_square)
    uniform_over_sphere = classmethod(uniform_over_sphere)
    uniform_sphere = classmethod(uniform_sphere)
    normal_dist = classmethod(normal_dist)
    grid = classmethod(grid)
    hexagonal = classmethod(hexagonal)
    triangular = classmethod(triangular)
    poissonprocess_square = classmethod(poissonprocess_square)
    poissonprocess_circle = classmethod(poissonprocess_circle)
    poissonprocess_inhomogeneus = classmethod(poissonprocess_inhomogeneus)
    cluster_square = classmethod(cluster_square)
    from_geopandas = classmethod(from_geopandas)
    draw = draw
    _affin_transformation = _affin_transformation
    rotation = rotation
    scaling = scaling
    traslation = traslation
    perturb = perturb
