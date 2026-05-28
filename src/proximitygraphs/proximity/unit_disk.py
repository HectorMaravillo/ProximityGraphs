"""Unit-disk graph construction.

This module implements unit-disk graphs, connecting two sites when their
Euclidean distance is at most a fixed radius. Unit-disk graphs are a standard
model for wireless communication, coverage, and geometric intersection graphs.

References
----------
Clark, B. N., Colbourn, C. J., & Johnson, D. S. (1990). Unit disk graphs.
Discrete Mathematics, 86(1-3), 165-177.
"""

from itertools import combinations

import numpy as np
from scipy.spatial.distance import pdist

from .base import ProximityGraph


class Unit_Disk(ProximityGraph):
    """
    Constructs a Unit Disk Graph.

    A Unit Disk Graph is a model where nodes are points in the plane, and an
    edge exists between two points if their Euclidean distance is less than or
    equal to a certain maximum distance, `dist_max`. This `dist_max` can be
    thought of as the "unit" distance.

    This type of graph is commonly used in wireless network modeling, where
    nodes represent devices and `dist_max` represents the communication range.

    Attributes
    ----------
    name : str
        The name of the graph, set to "Unit Disk Graph".
    details : str
        Additional details, including the maximum distance and whether the
        distance condition is inclusive.

    """

    # CONSTRUCTOR

    def __init__(self, setpoints, dist_max, closed=True):
        """
        Initializes a Unit_Disk object.

        Parameters
        ----------
        setpoints : SetPoints
            An object containing the set of points.
        dist_max : int or float
            The maximum distance for two points to be connected.
        closed : bool, optional
            If True (default), the distance condition is `<= dist_max`.
            If False, it is `< dist_max`.

        """
        if not isinstance(dist_max, (int, float)):
            raise TypeError("dist_max must be a number.")
        if dist_max < 0:
            raise ValueError("dist_max must be a non-negative number.")
        if not isinstance(closed, bool):
            raise TypeError("closed must be a boolean.")

        ProximityGraph.__init__(self, setpoints)
        self.name = "Unit Disk Graph"
        self.details = "distance max=" + str(dist_max) + ", closed=" + str(closed)
        self.inequality = self._ProximityGraph__closed_region(closed)
        self.__assign_edges(dist_max)
        self.graph.simplify()
        self._GeometricGraph__size()
        self._GeometricGraph__add_lengths()

    def __assign_edges(self, dist_max):
        """
        Connects all pairs of points whose distance is within `dist_max`.

        Parameters
        ----------
        dist_max : int or float
            The maximum distance threshold.

        """
        # Vectorized approach for smaller datasets
        if self.n <= self._GeometricGraph__limit_vec:
            pairs = list(combinations(range(self.n), 2))
            if not pairs:
                return
            pairs = np.array(pairs)
            dist_pairs = pdist(self.points)
            dist_disk = self.inequality(dist_pairs, dist_max)
            edges = pairs[dist_disk]
        else:  # Iterative approach for larger datasets
            edges = []
            for i in range(self.n):
                # Calculate distance from point i to all other points
                dist = np.linalg.norm(self.points - self.points[i], axis=1)
                # Find indices of points within the distance
                neighbors = np.where(self.inequality(dist, dist_max))[0]
                # Create edges, avoiding self-loops and duplicates
                for j in neighbors:
                    if i < j:
                        edges.append((i, j))
        self._GeometricGraph__graph.add_edges(edges)
