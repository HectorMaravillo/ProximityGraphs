"""Stepping-stone graph construction.

This module implements the stepping-stone graph, a proximity graph designed to
identify movement corridors from sparse spatial trajectories. Edges are kept
when the associated stepping-stone region contains no more than a prescribed
number of intermediate sites.

The model is useful when direct geometric adjacency should tolerate sparse or
incomplete observations while still preserving plausible corridors through a
point set.

References
----------
Kannangara, S., Tanin, E., Harwood, A., & Karunasekera, S. (2018). Stepping
Stone Graph for Public Movement Analysis. Proceedings of the 26th ACM
SIGSPATIAL International Conference on Advances in Geographic Information
Systems, 149-158.

Kannangara, S., Tanin, E., Harwood, A., & Karunasekera, S. (2019). Stepping
Stone Graph: A graph for finding movement corridors using sparse trajectories.
ACM Transactions on Spatial Algorithms and Systems, 5(4), 1-24.
"""

from itertools import combinations

import numpy as np
from igraph import Graph

from .base import ProximityGraph
from .delaunay import DelaunayG


class Stepping_Stone(ProximityGraph):
    """
    Constructs a Stepping Stone Graph.

    The Stepping Stone Graph is a proximity graph where an edge exists between
    two points p and q if a certain condition involving other points is met.
    Specifically, the edge (p, q) is included if there are at most k points z
    such that:
        dist(p, z)^d + dist(q, z)^d <= dist(p, q)^d
    where `dist` is the Euclidean distance, and `d` and `k` are parameters of
    the graph.

    This condition means that the "path" from p to q through any other point z
    is significantly longer than the direct path. The region defined by the
    inequality is an empty region criterion.

    - The parameter `d` controls the shape of the region. For d=2, the region
      is a circle with diameter pq.
    - The parameter `k` allows for a certain number of points to violate the
      empty region condition.

    For d >= 2, the Stepping Stone Graph is a subgraph of the Delaunay
    triangulation, so this implementation uses the Delaunay graph as a starting
    point to improve efficiency.

    Attributes
    ----------
    name : str
        The name of the graph, set to "Stepping Stone Graph".
    details : str
        Additional details about the graph, including parameters d and k.

    """

    # CONSTRUCTOR

    def __init__(self, setpoints, d=2, k=0, closed=False):
        """
        Initializes a Stepping_Stone object.

        Parameters
        ----------
        setpoints : SetPoints
            An object containing the set of points.
        d : int or float, optional
            The exponent in the distance condition (default is 2). Must be >= 1.
        k : int, optional
            The number of allowed points inside the empty region (default is 0).
            Must be a non-negative integer.
        closed : bool, optional
            Whether the empty region is closed (using <=) or open (using <)
            (default is False).

        """
        if not isinstance(d, (int, float)):
            raise TypeError("d must be a number.")
        if d < 1:
            raise ValueError("d must be greater than or equal to 1.")
        if not isinstance(k, int):
            raise TypeError("k must be an integer.")
        if k < 0:
            raise ValueError("k must be a non-negative integer.")
        if not isinstance(closed, bool):
            raise TypeError("closed must be a boolean.")

        ProximityGraph.__init__(self, setpoints)
        self.name = "Stepping Stone Graph"
        self.details = "d=" + str(d) + ", k=" + str(k) + ", closed=" + str(closed)
        self.__inequality = self._ProximityGraph__closed_region(closed)

        if d >= 1 and d < 2:
            pairs = combinations(range(self.n), 2)
        elif d >= 2:
            if self.n < self.points.shape[1] + 1:
                pairs = combinations(range(self.n), 2)
            else:
                g_delaunay = DelaunayG(self.setpoints)
                pairs = np.array(g_delaunay.graph.get_edgelist())

        self.__assign_edges(list(pairs), d, k)
        self.graph.simplify()
        self._GeometricGraph__size()
        self._GeometricGraph__add_lengths()

    @classmethod
    def from_graph(cls, geom_graph, d=2, k=0, closed=False):
        """
        Creates a Stepping_Stone graph from an existing GeometricGraph.

        This method is useful for building the graph on a pre-filtered set of
        edges, like a Delaunay triangulation.

        Parameters
        ----------
        geom_graph : GeometricGraph
            The base geometric graph.
        d : int or float, optional
            The exponent `d` for the graph construction (default is 2).
        k : int, optional
            The tolerance parameter `k` (default is 0).
        closed : bool, optional
            Whether the region is closed or open (default is False).

        Returns
        -------
        Stepping_Stone
            A new Stepping_Stone object.

        """
        ssg = cls.__new__(cls)
        ssg._ProximityGraph__check_parameter(d, range_min=1, strict=False)
        ssg.name = "Stepping Stone Graph"
        ssg.details = "d=" + str(d) + ", k=" + str(k) + ", closed=" + str(closed)
        ssg._GeometricGraph__setpoints = geom_graph.setpoints
        ssg._GeometricGraph__graph = Graph()
        ssg._GeometricGraph__graph.add_vertices(geom_graph.n)
        ssg.__inequality = ssg._ProximityGraph__closed_region(closed)
        pairs = np.array(geom_graph.graph.get_edgelist())
        ssg.__assign_edges(pairs, d, k)
        ssg.graph.simplify()
        ssg._GeometricGraph__size()
        ssg._GeometricGraph__add_lengths()
        return ssg

    # Methods
    def __assign_edges(self, pairs, d, k):
        """
        Tests pairs of points and adds edges based on the Stepping Stone
        criterion.

        Parameters
        ----------
        pairs : iterable
            An iterable of point index pairs to be tested.
        d : int or float
            The exponent in the distance condition.
        k : int
            The number of allowed points inside the empty region.

        """
        edges = []
        for pair in pairs:
            p = self.points[pair[0]]
            q = self.points[pair[1]]
            dist_pq = np.power(np.linalg.norm(p - q), d)
            dist_1 = np.power(np.linalg.norm(self.points - p, axis=1), d)
            dist_2 = np.power(np.linalg.norm(self.points - q, axis=1), d)
            # Check for each point z if dist(p,z)^d + dist(q,z)^d <= dist(p,q)^d
            empty_test = self.__inequality(dist_1 + dist_2, dist_pq)
            # Exclude the pair (p, q) themselves from the count
            empty_test = np.delete(empty_test, pair)
            # If the number of points inside the region is at most k, add edge
            if empty_test.sum() <= k:
                edges.append((pair[0], pair[1]))
        self._GeometricGraph__graph.add_edges(edges)
