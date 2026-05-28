"""Sigma-local graph construction.

This module implements sigma-local graphs, where a pair of sites is connected
according to a distance threshold scaled by local nearest-neighbor structure.
The resulting graph adapts to local point density rather than using a single
global distance threshold.

References
----------
Bose, P., Collette, S., Langerman, S., Maheshwari, A., Morin, P., & Smid, M.
(2010). Sigma-local graphs. Journal of Discrete Algorithms, 8(1), 15-23.
"""

from itertools import combinations

import numpy as np
from scipy.spatial.distance import pdist

from .base import ProximityGraph


class Sigma_Graph(ProximityGraph):
    """
    Constructs a sigma-Graph.

    The sigma-Graph is a proximity graph where an edge connects two points p and q
    if the two open disks of radius dist(p, q) / sigma centered at p and q are
    empty of other points. The parameter sigma >= 1 controls the size of these
    disks.

    - The edge (p, q) is in the graph if for all other points z:
        dist(p, z) > dist(p, q) / sigma
        dist(q, z) > dist(p, q) / sigma

    - When sigma = 1, the condition is that the open disks centered at p and q with
      radius dist(p, q) must be empty.
    - As sigma increases, the radius of the disks decreases, leading to more edges.

    Attributes
    ----------
    name : str
        The name of the graph, set to "sigma-Graph".
    details : str
        Additional details, including the value of sigma and whether the region is
        closed.

    """

    # CONSTRUCTOR

    def __init__(self, setpoints, sigma=1, closed=False):
        """
        Initializes a Sigma_Graph object.

        Parameters
        ----------
        setpoints : SetPoints
            An object containing the set of points.
        sigma : int or float, optional
            The parameter controlling the size of the empty disks (default is 1).
            Must be >= 1.
        closed : bool, optional
            Whether the empty region is closed (>=) or open (>) (default is False).

        """
        if not isinstance(sigma, (int, float)):
            raise TypeError("sigma must be a number.")
        if sigma < 1:
            raise ValueError("sigma must be greater than or equal to 1.")
        if not isinstance(closed, bool):
            raise TypeError("closed must be a boolean.")

        ProximityGraph.__init__(self, setpoints)
        self.name = "sigma-Graph"
        self.details = "sigma=" + str(sigma) + ", closed=" + str(closed)
        self.inequality = self._ProximityGraph__closed_region(closed)
        self.__assign_edges(sigma)
        self.graph.simplify()
        self._GeometricGraph__size()
        self._GeometricGraph__add_lengths()

    def __assign_edges(self, sigma):
        """
        Tests pairs of points and adds edges based on the sigma-Graph criterion.

        Parameters
        ----------
        sigma : int or float
            The sigma parameter for the graph.

        """
        if self.n < 2:
            return
        pairs = combinations(range(self.n), 2)
        edges = []

        if self.n <= self._GeometricGraph__limit_vec:
            pairs = np.array(list(pairs))
            p = self.points[pairs[:, 0]]
            q = self.points[pairs[:, 1]]
            dist_sigma = pdist(self.points) / sigma
            for i in np.arange(pairs.shape[0]):
                # Check empty disk around p
                dist_1 = np.linalg.norm(self.points - p[i], axis=1)
                empty_test_1 = self.inequality(dist_1, dist_sigma[i])
                empty_test_1 = np.delete(empty_test_1, pairs[i])
                if not np.any(empty_test_1):
                    # Check empty disk around q
                    dist_2 = np.linalg.norm(self.points - q[i], axis=1)
                    empty_test_2 = self.inequality(dist_2, dist_sigma[i])
                    empty_test_2 = np.delete(empty_test_2, pairs[i])
                    if not np.any(empty_test_2):
                        edges.append(pairs[i])
        else:  # Iterative approach for larger datasets
            for pair in pairs:
                p = self.points[pair[0]]
                q = self.points[pair[1]]
                dist_sigma = np.linalg.norm(p - q) / sigma
                # Check empty disk around p
                dist_1 = np.linalg.norm(self.points - p, axis=1)
                empty_test_1 = self.inequality(dist_1, dist_sigma)
                empty_test_1 = np.delete(empty_test_1, pair)
                if not np.any(empty_test_1):
                    # Check empty disk around q
                    dist_2 = np.linalg.norm(self.points - q, axis=1)
                    empty_test_2 = self.inequality(dist_2, dist_sigma)
                    empty_test_2 = np.delete(empty_test_2, pair)
                    if not np.any(empty_test_2):
                        edges.append((pair[0], pair[1]))
        self._GeometricGraph__graph.add_edges(edges)
