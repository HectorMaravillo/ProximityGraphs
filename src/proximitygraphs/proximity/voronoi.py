"""Voronoi graph construction.

This module builds the site-adjacency graph induced by the Voronoi diagram of
a finite point set. Two input points are connected when their Voronoi regions
share a ridge. In general position this graph is the edge graph of the
Delaunay triangulation, the planar dual of the Voronoi diagram.

References
----------
Aurenhammer, F., & Klein, R. (2000). Voronoi diagrams. In Handbook of
Computational Geometry, 201-290. Elsevier Science.
"""

from scipy.spatial import Voronoi as ScipyVoronoi

from .base import ProximityGraph


class Voronoi(ProximityGraph):
    """
    Constructs the Voronoi site-adjacency graph of a set of points.

    The Voronoi diagram partitions the plane into regions containing all
    locations closest to each input point. This graph connects two original
    input points whenever their Voronoi cells share a ridge.

    This implementation uses `scipy.spatial.Voronoi` to compute the diagram and
    stores the graph over the original input points, using `ridge_points` as the
    edge list.

    Attributes
    ----------
    name : str
        The name of the graph, set to "Voronoi Diagram".

    """

    # CONSTRUCTOR
    def __init__(self, setpoints):
        """
        Initializes a Voronoi object.

        The constructor computes the Voronoi diagram and adds one edge for each
        pair of input sites whose Voronoi regions share a ridge.

        Parameters
        ----------
        setpoints : SetPoints
            An object containing the set of points.

        """
        ProximityGraph.__init__(self, setpoints)
        self.name = "Voronoi Diagram"
        voronoi = ScipyVoronoi(setpoints.points)
        self.graph.add_edges([tuple(edge) for edge in voronoi.ridge_points])
        self.graph.simplify()
        self._GeometricGraph__size()
        self._GeometricGraph__add_lengths()
