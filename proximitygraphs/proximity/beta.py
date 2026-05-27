"""Beta-skeleton graph construction.

This module implements beta-skeleton empty-region graphs. For each pair of
sites p and q, an edge is added when the beta-dependent region associated with
the pair is empty of other sites.

The Gabriel graph and relative-neighborhood graph special cases live in
``gabriel.py`` and ``relateve.py`` respectively, but are re-exported here for
backward compatibility.

References
----------
Gabriel, K. R., & Sokal, R. R. (1969). A new statistical approach to
geographic variation analysis. Systematic Zoology, 18(3), 259-278.

Toussaint, G. T. (1980). The relative neighbourhood graph of a finite planar
set. Pattern Recognition, 12(4), 261-268.

Kirkpatrick, D. G., & Radke, J. D. (1985). A framework for computational
morphology. In Computational Geometry, 217-248.

Jaromczyk, J. W., & Toussaint, G. T. (2002). Relative neighborhood graphs and
their relatives. Proceedings of the IEEE, 80(9), 1502-1517.
"""

import warnings
from itertools import combinations
from typing import TYPE_CHECKING

import numpy as np
from igraph import Graph

from .base import ProximityGraph
from .delaunay import DelaunayG

if TYPE_CHECKING:
    from .gabriel import GG
    from .relateve import RNG


class Beta_Skeleton(ProximityGraph):
    """
    Constructs the beta-skeleton of a set of points.

    Two points p and q are connected if the beta-dependent region associated with
    the pair is empty of other points. The shape of the region depends on the
    value of beta and the specified type.

    Attributes
    ----------
    name : str
        The name of the graph, set to "beta-Skeleton".
    details : str
        Additional information including beta, closed, and type_region.
    """

    matrix_r = np.array([[0, -1], [1, 0]])

    # CONSTRUCTOR
    def __init__(self, setpoints, beta=1.5, type_region="lune", closed=False):
        """
        Initializes a Beta_Skeleton object.

        Parameters
        ----------
        setpoints : SetPoints
            An object containing the set of points.
        beta : float, optional
            The parameter that defines the shape of the empty region. Must be >= 0.
        type_region : str, optional
            The type of empty region to use. Must be 'lune', 'circle',
            or 'intersection'.
        closed : bool, optional
            Whether to use closed or open regions for edge inclusion.
            Default is False (open).
        """
        self._ProximityGraph__check_parameter(beta, range_min=0, strict=True)
        ProximityGraph.__init__(self, setpoints)
        self.name = "beta-Skeleton"
        self.details = f"beta={beta}, closed={closed}, type={type_region}"
        pairs = self.__defined_pairs(beta, type_region, closed)
        self.__assign_edges(pairs, beta, closed)
        self.graph.simplify()
        self._GeometricGraph__size()
        self._GeometricGraph__add_lengths()

    @classmethod
    def from_graph(cls, geom_graph, beta=1.5, type_region="lune", closed=False):
        """
        Creates an instance of Beta_Skeleton from an existing GeometricGraph.

        Parameters
        ----------
        geom_graph : GeometricGraph
            An existing geometric graph from which to construct the beta-skeleton.
        beta : float, optional
            The parameter that defines the shape of the empty region. Must be >= 0.
        type_region : str, optional
            The type of empty region to use. Must be 'lune', 'circle',
            or 'intersection'.
        closed : bool, optional
            Whether to use closed or open regions for edge inclusion.
            Default is False (open).
        """
        skeleton = cls.__new__(cls)
        skeleton._ProximityGraph__check_parameter(beta, range_min=0, strict=True)
        skeleton.name = "beta-Skeleton"
        skeleton.details = (
            f"beta={beta}, closed={closed}, type={type_region}, (from graph)"
        )
        skeleton._GeometricGraph__setpoints = geom_graph.setpoints
        skeleton._GeometricGraph__graph = Graph()
        skeleton._GeometricGraph__graph.add_vertices(geom_graph.n)
        pairs = np.array(geom_graph.graph.get_edgelist())
        if beta < 1:
            if type_region != "intersection":
                warnings.warn(
                    (
                        f"For beta < 1, the region type {type_region!r} is undefined. "
                        "Use type_region='intersection' instead."
                    ),
                    stacklevel=2,
                )
            skeleton.__empty_region = lambda p, q: skeleton.__intersection(p, q, beta)
            skeleton.__test = lambda test_1, test_2: test_1 * test_2
        elif beta >= 1:
            if type_region not in ["lune", "circle"]:
                raise TypeError(
                    "'type_region' must be 'lune' or 'circle' when beta > 1."
                )
            if type_region == "lune":
                skeleton.__empty_region = lambda p, q: skeleton.__lune(p, q, beta)
                skeleton.__test = lambda test_1, test_2: test_1 * test_2
            elif type_region == "circle":
                skeleton.__empty_region = lambda p, q: skeleton.__circle(p, q, beta)
                skeleton.__test = lambda test_1, test_2: test_1 + test_2
        skeleton.__assign_edges(pairs, beta, closed)
        skeleton.graph.simplify()
        skeleton._GeometricGraph__size()
        skeleton._GeometricGraph__add_lengths()
        return skeleton

        # Methods

    def __pairs_by_combinations(self):
        return np.array(list(combinations(range(self.n), 2)))

    def __pairs_by_delaunay(self):
        g_delaunay = DelaunayG(self.setpoints)
        return np.array(g_delaunay.graph.get_edgelist())

    def __defined_pairs(self, beta, type_region, closed):
        if beta < 1:
            if type_region != "intersection":
                warnings.warn(
                    (
                        f"For beta < 1, the region type {type_region!r} is undefined. "
                        "Use type_region='intersection' instead."
                    ),
                    stacklevel=2,
                )
            pairs = self.__pairs_by_combinations()
            self.__empty_region = lambda p, q: self.__intersection(p, q, beta)
            self.__test = lambda test_1, test_2: test_1 * test_2
        elif beta >= 1:
            if type_region not in ["lune", "circle"]:
                raise TypeError(
                    "'type_region' must be 'lune' or 'circle' when beta > 1."
                )
            if beta == 1 and closed is False:
                pairs = self.__pairs_by_combinations()
            else:
                pairs = self.__pairs_by_delaunay()
            if type_region == "lune":
                self.__empty_region = lambda p, q: self.__lune(p, q, beta)
                self.__test = lambda test_1, test_2: test_1 * test_2
            elif type_region == "circle":
                self.__empty_region = lambda p, q: self.__circle(p, q, beta)
                self.__test = lambda test_1, test_2: test_1 + test_2
        return pairs

    def __assign_edges(self, pairs, beta, closed):
        p = self.points[pairs[:, 0]]
        q = self.points[pairs[:, 1]]
        if beta < 1:
            radius = np.linalg.norm(p - q, axis=1) / (2 * beta)
        else:
            radius = np.linalg.norm(p - q, axis=1) * beta / 2
        center_1, center_2 = self.__empty_region(p, q)
        edges = []
        for i in np.arange(pairs.shape[0]):
            dist_1 = np.linalg.norm(self.points - center_1[i], axis=1)
            dist_2 = np.linalg.norm(self.points - center_2[i], axis=1)
            if closed:
                empty_test_1 = dist_1 <= radius[i]
                empty_test_2 = dist_2 <= radius[i]
            else:
                empty_test_1 = dist_1 < radius[i]
                empty_test_2 = dist_2 < radius[i]
            empty_test = self.__test(empty_test_1, empty_test_2)
            empty_test = np.delete(empty_test, pairs[i])
            if not np.any(empty_test):
                edges.append(pairs[i])
        self.graph.add_edges(edges)

    def __intersection(cls, p, q, beta):
        aux_1 = (p + q) / 2
        aux_2 = (q - p) @ cls.matrix_r.T * np.sqrt(1 - np.power(beta, 2)) / (2 * beta)
        center_1 = aux_1 + aux_2
        center_2 = aux_1 - aux_2
        return center_1, center_2

    def __circle(cls, p, q, beta):
        aux_1 = (p + q) / 2
        aux_2 = (q - p) @ cls.matrix_r.T * np.sqrt(np.power(beta, 2) - 1) / 2
        center_1 = aux_1 + aux_2
        center_2 = aux_1 - aux_2
        return center_1, center_2

    def __lune(cls, p, q, beta):
        beta_aux = beta / 2
        aux = 1 - beta_aux
        center_1 = p * beta_aux + aux * q
        center_2 = q * beta_aux + aux * p
        return center_1, center_2


__all__ = [
    "GG",
    "RNG",
    "Beta_Skeleton",
]


def __getattr__(name):
    if name == "GG":
        from .gabriel import GG

        return GG
    if name == "RNG":
        from .relateve import RNG

        return RNG
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
