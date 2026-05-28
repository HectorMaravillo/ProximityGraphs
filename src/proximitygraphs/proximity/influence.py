"""Sphere-of-influence graph construction.

This module implements the sphere-of-influence graph. Each site receives an
influence radius determined by its nearest neighbor, and two sites are joined
when their influence spheres overlap.

Sphere-of-influence graphs provide a density-sensitive proximity model and
have been studied both for theory and for applications in spatial pattern
analysis.

References
----------
Chalker, T. K., Godbole, A. P., Hitczenko, P., Radcliff, J., & Ruehr, O. G.
(1999). On the size of a random sphere of influence graph. Advances in Applied
Probability, 31(3), 596-609.

Toussaint, G. T. (2014). The sphere of influence graph: Theory and
applications. International Journal of Information Technology & Computer
Science, 14(2), 37-42.
"""

from itertools import combinations

import numpy as np
from scipy.spatial.distance import pdist

from .base import ProximityGraph


class SIG(ProximityGraph):
    """
    Constructs the Sphere of Influence Graph (SIG).

    The SIG is defined on a set of points in a metric space. For each point p,
    consider an open ball (or "sphere of influence") centered at p with radius
    equal to the distance to its nearest neighbor. An edge exists between two
    points p and q if their spheres of influence intersect.

    Mathematically, an edge (p, q) is in the SIG if:
        dist(p, q) <= radius(p) + radius(q)
    where radius(p) is the distance from p to its nearest neighbor.

    The SIG is related to the concept of territoriality and is used in various
    fields, including pattern recognition and spatial analysis.

    Attributes
    ----------
    name : str
        The name of the graph, set to "Sphere Influence Graph".
    details : str
        Additional details, including whether the intersection condition is
        inclusive.

    """

    # CONSTRUCTOR

    def __init__(self, setpoints, closed=False):
        """
        Initializes a SIG object.

        Parameters
        ----------
        setpoints : SetPoints
            An object containing the set of points.
        closed : bool, optional
            If False (default), the intersection is based on open balls (<).
            If True, it is based on closed balls (<=).

        """
        ProximityGraph.__init__(self, setpoints)
        if not isinstance(closed, bool):
            raise TypeError("closed must be a boolean.")
        self.name = "Sphere Influence Graph"
        self.details = "closed=" + str(closed)
        self.inequality = self._ProximityGraph__closed_region(closed)
        self.__assign_edges()
        self.graph.simplify()
        self._GeometricGraph__size()
        self._GeometricGraph__add_lengths()

    def __assign_edges(self):
        """
        Connects pairs of points whose spheres of influence intersect.

        This method first computes the nearest neighbor distance for each point,
        which defines the radius of its sphere of influence. Then, it checks
        all pairs of points for intersection.

        """
        if self.n < 2:
            return
        pairs = combinations(range(self.n), 2)
        # Get the radius for each point's sphere of influence
        dist_min = self._GeometricGraph__dist_nearest()

        # Vectorized approach for smaller datasets
        if self.n <= self._GeometricGraph__limit_vec:
            pairs = np.array(list(pairs))

            def dist_min_sum(p, q):
                return dist_min[p] + dist_min[q]

            dist_min_sum_vec = np.vectorize(dist_min_sum)
            # Check if distance between pairs is less than sum of radii
            influence = self.inequality(
                pdist(self.points), dist_min_sum_vec(pairs[:, 0], pairs[:, 1])
            )
            edges = pairs[influence]
        else:  # Iterative approach for larger datasets
            edges = []
            for p, q in pairs:
                dist = np.linalg.norm(self.points[p] - self.points[q])
                if self.inequality(dist, dist_min[p] + dist_min[q]):
                    edges.append((p, q))
        self.graph.add_edges(edges)
