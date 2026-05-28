"""Nearest-neighbor graph construction.

This module implements k-nearest-neighbor graphs over finite point sets. Each
site is connected to its k closest sites, producing a local graph that is often
used as a sparse neighborhood model for clustering, approximation, and
geometric network analysis.

References
----------
Eppstein, D., Paterson, M. S., & Yao, F. F. (1997). On nearest-neighbor
graphs. Discrete & Computational Geometry, 17, 263-282.
"""

import numpy as np
from scipy.spatial.distance import cdist

from .base import ProximityGraph


class NNG(ProximityGraph):
    """
    Constructs the k-Nearest Neighbor Graph (k-NNG).

    In a k-NNG, each vertex is connected to its `k` nearest neighbors. The
    resulting graph can be directed (where an edge (p, q) exists if q is one
    of the k nearest neighbors of p) or undirected (where an edge exists if
    either p is a k-NN of q or q is a k-NN of p).

    This implementation constructs a directed k-NNG and then simplifies it,
    effectively creating an undirected graph where an edge exists if the
    relationship is reciprocal or if one is a neighbor of the other.

    The Minimum Spanning Tree of the points is always a subgraph of the NNG.

    Attributes
    ----------
    name : str
        The name of the graph, set to "Nearest Neighbor Graph".
    details : str
        Additional details, including the value of k.

    """

    # CONSTRUCTOR

    def __init__(self, setpoints, k=1):
        """
        Initializes a NNG object.

        Parameters
        ----------
        setpoints : SetPoints
            An object containing the set of points.
        k : int, optional
            The number of nearest neighbors to connect (default is 1). Must be
            a positive integer.

        """
        if not isinstance(k, int):
            raise TypeError("k must be an integer.")
        if k < 1:
            raise ValueError("k must be a positive integer.")

        ProximityGraph.__init__(self, setpoints)
        self.name = "Nearest Neighbor Graph"
        self.details = "k=" + str(k)
        self.__assign_edges(k)
        self.graph.simplify()
        self._GeometricGraph__size()
        self._GeometricGraph__add_lengths()

    def __assign_edges(self, k):
        """
        Finds the k-nearest neighbors for each point and adds the corresponding
        edges to the graph.

        The method handles both small and large numbers of points efficiently.
        For a small number of points, it uses a distance matrix. For a larger
        number, it iterates through each point to avoid creating a large matrix.

        Parameters
        ----------
        k : int
            The number of nearest neighbors to find for each point.

        """
        if self.n == 0:
            return
        edges = []

        if self.n <= self._GeometricGraph__limit_vec:
            dist_matrix = cdist(self.points, self.points)
            np.fill_diagonal(dist_matrix, np.inf)
            for _ in range(k):
                arg_min = np.argmin(dist_matrix, axis=1)
                edges.extend(list(enumerate(arg_min)))
                dist_matrix[np.arange(self.n), arg_min] = np.inf
        else:
            for i in range(self.n):
                dist = np.linalg.norm(self.points - self.points[i], axis=1)
                dist[i] = np.inf
                for _ in range(k):
                    arg_min = np.argmin(dist)
                    edges.append((i, arg_min))
                    dist[arg_min] = np.inf
        self.graph.add_edges(edges)
