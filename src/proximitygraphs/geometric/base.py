"""Embedded graph representation and geometric graph operations.

This module defines ``GeometricGraph``, the base class for graphs whose
vertices have coordinates. It wraps an ``igraph.Graph`` with point coordinates,
edge lengths, orientation statistics, drawing utilities, graph-set operations,
GIS export helpers, and entropy-based summaries.

References
----------
Csardi, G., & Nepusz, T. (2006). The igraph software package for complex
network research. InterJournal, Complex Systems, 1695.
"""

import igraph as ig
import numpy as np

from ..points import SetPoints
from .analysis import (
    _GeometricGraph__add_lengths,
    _GeometricGraph__add_orientation,
    _GeometricGraph__dist_nearest,
    _GeometricGraph__size,
    copy,
    entropy,
)
from .constructors import complete, from_graph, random_graph
from .drawing import draw, draw_orientation
from .gis import save, to_gpd_lines, to_gpd_polygons
from .operations import (
    _check_setpoints_compatibility,
    _prepare_graphs_for_operation,
    difference,
    intersection,
    recovering,
    symmetric_difference,
    union,
)


class GeometricGraph:
    """
    Represents a graph embedded in a geometric space.

    Vertices have coordinates, and the graph structure is typically derived
    from the spatial relationships between these points (e.g., proximity graphs).
    This class provides methods for graph construction, modification, analysis
    of geometric and topological properties, and visualization.

    Attributes:
        points (numpy.ndarray): A NumPy array of point coordinates (n x dim).
        setpoints (SetPoints): The SetPoints object managing the vertex coordinates.
        n (int): The number of vertices in the graph.
        m (int): The number of edges in the graph.
        cc (int): The number of connected components in the graph.
        f (int): The number of faces in a planar embedding (calculated by
            Euler's formula).
        graph (igraph.Graph): The underlying igraph Graph object.
        name (str): A name for the graph (e.g., "Gabriel Graph").
        details (str): Additional details or parameters used to construct the graph.
        degrees (numpy.ndarray): The degree sequence of the graph.
        lengths (numpy.ndarray): An array of Euclidean lengths for all edges.
        orientation (numpy.ndarray): Orientations (angles in degrees) for all
            edges.
    """

    # ATTRIBUTES
    @property
    def points(self):
        """numpy.ndarray: Coordinates of vertices as an n x dim array."""
        return self.__setpoints.points

    @property
    def setpoints(self):
        """SetPoints: Underlying object containing vertex coordinates and RNG."""
        return self.__setpoints

    @property
    def n(self):
        """int: The number of vertices in the graph."""
        return self.__setpoints.n

    @property
    def m(self):
        """int: The number of edges in the graph."""
        return self.__m

    @property
    def cc(self):
        """int: The number of connected components in the graph."""
        return len(self.graph.connected_components())

    @property
    def f(self):
        """int: The number of faces, calculated using
        Euler's formula: V-E+F=C+1for general planar graphs,
        or V-E+F=1 for a single connected component on a sphere/plane
        if graph is connected).
        Here it's simplified as C - V + E + 1, assuming one exterior face.
        """
        return self.cc - self.n + self.m + 1

    @property
    def graph(self):
        """igraph.Graph: The underlying igraph graph object."""
        return self.__graph

    @property
    def name(self):
        """str: The name of the geometric graph type."""
        return self.__name

    @name.setter
    def name(self, new_name):
        self.__name = new_name

    @property
    def details(self):
        return self.__details

    @details.setter
    def details(self, new_details):
        self.__details = new_details

    @property
    def degrees(self):
        """numpy.ndarray: The degree distribution of the graph.
        The i-th element is the count of vertices with degree i+1.
        """
        degrees = self.graph.degree()
        if not degrees:
            return np.array([])
        degrees_sequence = [
            degrees.count(i) for i in range(1, max(degrees) + 1 if degrees else 1)
        ]
        return np.array(degrees_sequence)

    @property
    def lengths(self):
        """numpy.ndarray: Euclidean lengths of all edges in the graph.

        Returns an empty array if the graph has no edges.
        """
        if self.m == 0:
            return np.array([])
        else:
            if "dist_eucl" not in self.graph.es.attribute_names():
                self.__add_lengths()
            return np.array(self.graph.es["dist_eucl"])

    @property
    def orientation(self):
        """numpy.ndarray: An array containing the orientation
        (angle in degrees, typically CCW from positive x-axis) of all edges.
        Calculated on demand if not already present. Returns an empty array if no edges
        or if not applicable.
        """
        if (
            not hasattr(self.graph, "es")
            or "orientation" not in self.graph.es.attribute_names()
        ):
            self.__add_orientation()
        if (
            hasattr(self.graph, "es")
            and "orientation" in self.graph.es.attribute_names()
        ):
            return np.array(self.graph.es["orientation"])
        return np.array([])

    __limit_vec = 20000

    def __init__(self, setpoints):
        if not isinstance(setpoints, SetPoints):
            raise TypeError("Input 'setpoints' must be an instance of SetPoints.")
        self.__setpoints = setpoints
        self.__graph = ig.Graph()
        self.__graph.add_vertices(self.n)
        self.__m = 0
        self.__name = "Geometric Graph"
        self.__details = ""

    complete = classmethod(complete)
    from_graph = classmethod(from_graph)
    random_graph = classmethod(random_graph)
    copy = copy
    _GeometricGraph__size = _GeometricGraph__size
    _GeometricGraph__add_lengths = _GeometricGraph__add_lengths
    _GeometricGraph__add_orientation = _GeometricGraph__add_orientation
    entropy = entropy
    draw_orientation = draw_orientation
    draw = draw
    _GeometricGraph__dist_nearest = _GeometricGraph__dist_nearest
    _prepare_graphs_for_operation = _prepare_graphs_for_operation
    _check_setpoints_compatibility = _check_setpoints_compatibility
    union = union
    intersection = intersection
    difference = difference
    symmetric_difference = symmetric_difference
    recovering = recovering
    save = save
    to_gpd_lines = to_gpd_lines
    to_gpd_polygons = to_gpd_polygons
