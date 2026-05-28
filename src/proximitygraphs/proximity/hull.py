"""Convex hull graph construction.

This module builds the boundary graph of the convex hull of a finite point
set. The convex hull is the smallest convex set containing all input points and
acts as a limiting case for several proximity graph families, including special
gamma-neighborhood configurations.

References
----------
De Berg, M., Cheong, O., Van Kreveld, M., & Overmars, M. (2008).
Computational Geometry: Algorithms and Applications. Springer.
"""

from scipy.spatial import ConvexHull

from ..points import SetPoints
from .base import ProximityGraph


class Convex_Hull(ProximityGraph):
    """
    Constructs the convex hull of a set of points.

    The convex hull of a set of points P is the smallest convex polygon that
    contains all the points in P. The vertices of this polygon are a subset of
    the points in P.

    This implementation uses `scipy.spatial.ConvexHull` to compute the hull.

    Attributes
    ----------
    name : str
        The name of the graph, set to "Convex Hull".

    """

    # CONSTRUCTOR

    def __init__(self, setpoints):
        """
        Initializes a Convex_Hull object.

        The constructor computes the convex hull and adds the edges forming the
        boundary of the hull to the graph.

        Parameters
        ----------
        setpoints : SetPoints
            An object containing the set of points.

        """
        ProximityGraph.__init__(self, setpoints)
        self.name = "Convex Hull"
        hull = ConvexHull(setpoints.points)
        self.graph.add_edges(hull.simplices)
        self.graph.simplify()
        self._GeometricGraph__size()
        self._GeometricGraph__add_lengths()

    # Methods
    def vertices(self):
        """
        Returns the vertices of the convex hull.

        This method identifies the vertices that form the convex hull from the
        graph representation. In a 2D convex hull, these vertices will have a
        degree of 2.

        Returns
        -------
        SetPoints
            A new SetPoints object containing only the vertices of the hull.

        """
        convex_hull_v = self.graph.vs.select(_degree=2).indices
        return SetPoints(self.points[convex_hull_v])
