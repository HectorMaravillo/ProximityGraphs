"""Euclidean minimum spanning tree construction.

This module constructs the minimum spanning tree over a finite Euclidean point
set. The Euclidean MST is a sparse proximity structure and, in the plane under
standard assumptions, is contained in the Delaunay triangulation. This
implementation uses that relationship by computing a Delaunay graph first and
then extracting a weighted spanning tree.

References
----------
Devroye, L. (1988). The expected size of some graphs in computational
geometry. Computers & Mathematics with Applications, 15(1), 53-64.

De Berg, M., Cheong, O., Van Kreveld, M., & Overmars, M. (2008).
Computational Geometry: Algorithms and Applications. Springer.
"""

from .base import ProximityGraph
from .delaunay import DelaunayG


class MST(ProximityGraph):
    """
    Constructs the Minimum Spanning Tree (MST) of a set of points.

    The MST is a subgraph of a connected, edge-weighted graph that connects
    all the vertices together, without any cycles and with the minimum possible
    total edge weight.

    For a set of points in a Euclidean space, the MST is based on the complete
    graph where edge weights are the Euclidean distances between points. It is
    a known property that the Euclidean MST is a subgraph of the Delaunay
    triangulation. This implementation leverages that by first computing the
    Delaunay graph and then finding the MST on it, which is more efficient
    than computing it on the complete graph.

    Attributes
    ----------
    name : str
        The name of the graph, set to "Minimum Spanning Tree".

    """

    # CONSTRUCTOR

    def __init__(self, setpoints):
        """
        Initializes an MST object.

        The constructor first builds the Delaunay triangulation of the points,
        then computes the minimum spanning tree of this graph.

        Parameters
        ----------
        setpoints : SetPoints
            An object containing the set of points.

        """
        ProximityGraph.__init__(self, setpoints)
        self.name = "Minimum Spanning Tree"
        d = DelaunayG(setpoints)
        mst = d.graph.spanning_tree(weights=d.graph.es["dist_eucl"])
        self._GeometricGraph__graph = mst
        self.graph.simplify()
        self._GeometricGraph__size()
