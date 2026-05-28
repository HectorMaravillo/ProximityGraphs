"""Delaunay graph construction.

This module builds the edge graph of the Delaunay triangulation of a finite
point set. Delaunay triangulations are dual to Voronoi diagrams and satisfy an
empty-circumcircle property: no input point lies inside the circumcircle of a
triangle in the triangulation.

Several proximity graphs implemented in this library can be computed by
testing only Delaunay candidate edges in regimes where the relevant graph is
known to be a Delaunay subgraph.

References
----------
Aurenhammer, F., & Klein, R. (2000). Voronoi diagrams. In Handbook of
Computational Geometry, 201-290. Elsevier Science.

De Berg, M., Cheong, O., Van Kreveld, M., & Overmars, M. (2008). Delaunay
triangulations. In Computational Geometry: Algorithms and Applications,
191-218. Springer.
"""

from scipy.spatial import Delaunay

from .base import ProximityGraph


class DelaunayG(ProximityGraph):
    """
    Constructs the Delaunay triangulation of a set of points.

    The Delaunay triangulation is a fundamental structure in computational
    geometry. For a set P of points in a plane, the Delaunay triangulation DT(P)
    is a triangulation such that no point in P is inside the circumcircle of
    any triangle in DT(P). This is known as the "empty circle" property.

    This implementation uses `scipy.spatial.Delaunay` to compute the
    triangulation.

    Attributes
    ----------
    name : str
        The name of the graph, set to "Delaunay Triangulation".

    """

    # CONSTRUCTOR
    def __init__(self, setpoints):
        """
        Initializes a DelaunayG object.

        The constructor computes the Delaunay triangulation and adds the
        corresponding edges to the graph.

        Parameters
        ----------
        setpoints : SetPoints
            An object containing the set of points.

        """
        ProximityGraph.__init__(self, setpoints)
        self.name = "Delaunay Triangulation"
        delaunay = Delaunay(setpoints.points)
        edges = []
        for tri in delaunay.simplices:
            edges.append((tri[0], tri[1]))
            edges.append((tri[1], tri[2]))
            edges.append((tri[0], tri[2]))
        self.graph.add_edges(edges)
        self.graph.simplify()
        self._GeometricGraph__size()
        self._GeometricGraph__add_lengths()
