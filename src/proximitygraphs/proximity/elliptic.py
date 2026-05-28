"""Elliptic Gabriel and empty-ellipse graph construction.

This module implements an elliptic Gabriel graph variant, replacing circular
empty regions with ellipse-based tests. Empty-ellipse graphs generalize several
classical proximity ideas by controlling adjacency through ellipse geometry
rather than disk geometry.

References
----------
Park, J. C., Shin, H., & Choi, B. K. (2006). Elliptic Gabriel graph for
finding neighbors in a point set and its application to normal vector
estimation. Computer-Aided Design, 38(6), 619-626.

Devillers, O., Erickson, J., & Goaoc, X. (2008). Empty-ellipse graphs. 19th
Annual ACM-SIAM Symposium on Discrete Algorithms, 1249-1256.
"""

from itertools import combinations

import numpy as np
from igraph import Graph

from .base import ProximityGraph
from .beta import GG


class Elliptic_GabrielG(ProximityGraph):
    """
    Constructs the Elliptic Gabriel Graph (EGG) of a set of points.

    Two points p and q are connected if the ellipse with foci at p and q and
    major axis length alpha * ||p - q|| contains no other points.

    Attributes
    ----------
    name : str
        The name of the graph, set to "Elliptic Gabriel Graph".
    details : str
        Additional information including alpha.
    """

    def __init__(self, setpoints, alpha=1.5, closed=False):
        """
        Initializes an Elliptic_GabrielG object.

        Parameters
        ----------
        setpoints : SetPoints
            An object containing the set of points.
        alpha : float, optional
            The elongation factor of the ellipse. Must be >= 0.
        """
        self._ProximityGraph__check_parameter(alpha, range_min=0, strict=True)
        ProximityGraph.__init__(self, setpoints)
        self.name = "Elliptic Gabriel Graph"
        self.details = "alpha=" + str(alpha)
        if alpha < 1:
            pairs = np.array(list(combinations(range(self.n), 2)))
        else:
            # Use GG to reduce candidate edges
            g_gabriel = GG(self.setpoints, closed)
            pairs = np.array(g_gabriel.graph.get_edgelist())
        self.__inequality = self._ProximityGraph__closed_region(closed)
        self.__assign_edges(pairs, alpha)
        self.graph.simplify()
        self._GeometricGraph__size()
        self._GeometricGraph__add_lengths()

    def __assign_edges(self, pairs, alpha):
        """
        Assigns edges based on the elliptical empty region condition.

        Parameters
        ----------
        alpha : float
            The elliptic elongation factor.
        """
        edges = []
        for pair in pairs:
            p = self.points[pair[0]]
            q = self.points[pair[1]]
            # Punto medio entre p y q
            mean_point = np.mean([p, q], axis=0)
            # Vector del punto medio hacia hacia q
            v = q - mean_point
            # Dirección de la recta pq (normalización v)
            v_n = v / np.linalg.norm(v)
            # angle to rotate vector to z axis
            angle = -np.arctan2(v_n[1], v_n[0])
            # Construct the 2D rotation matrixes
            M = np.array(
                [[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]]
            )
            # Rotación
            rotation = (self.points - mean_point) @ M.T
            # Eliminar p y q
            rotation = np.delete(rotation, pair, axis=0)

            x = rotation[:, 0]
            y = rotation[:, 1]

            dist_to_foci = np.power(x, 2) + np.power((y / alpha), 2)
            dist_pq = np.linalg.norm(p - q)
            dist_pq_sqr = np.power(dist_pq / 2, 2)

            # Check for each point z if x**2+(y/alpha)**2 <= dist(p,q)**2
            empty_test = self.__inequality(dist_to_foci, dist_pq_sqr)

            if not np.any(empty_test):
                edges.append(pair)
        self.graph.add_edges(edges)

    @classmethod
    def from_graph(cls, geom_graph, alpha, closed):
        """
        Creates an Elliptic Gabriel Graph from an existing GeometricGraph.

        Parameters
        ----------
        geom_graph : GeometricGraph
            The geometric graph to use as a base.
        alpha : float
            Elongation factor (must be >= 1).

        Returns
        -------
        Elliptic_GabrielG
            A new Elliptic_GabrielG instance.
        """
        egg = cls.__new__(cls)
        egg._ProximityGraph__check_parameter(alpha, range_min=0, strict=False)
        egg.name = "Elliptic Gabriel Graph"
        egg.details = "alpha=" + str(alpha)
        egg._GeometricGraph__setpoints = geom_graph.setpoints
        egg._GeometricGraph__graph = Graph()
        egg._GeometricGraph__graph.add_vertices(geom_graph.n)

        pairs = np.array(geom_graph.graph.get_edgelist())
        egg.__inequality = egg._ProximityGraph__closed_region(closed)
        egg.__assign_edges(pairs, alpha)
        egg.graph.simplify()
        egg._GeometricGraph__size()
        egg._GeometricGraph__add_lengths()
        return egg
