"""Base class for proximity graph constructions.

Proximity graphs model local structure in finite metric point sets by adding
edges according to geometric neighborhood rules. They are widely used in
computational geometry, spatial analysis, clustering, manifold learning, and
shape description because they turn metric data into sparse graph structure.

The concrete graph classes in this package specialize this base class with
empty-region tests, nearest-neighbor relations, disk intersections, Delaunay
candidate pruning, and other geometric predicates.

References
----------
Cimikowski, R. J. (1992). Properties of some Euclidean proximity graphs.
Pattern Recognition Letters, 13(6), 417-423.

Mathieson, L., & Moscato, P. (2019). An introduction to proximity graphs. In
Business and Consumer Analytics: New Ideas, 213-233. Springer.
"""

import numpy as np

from ..geometricgraphs import GeometricGraph


class ProximityGraph(GeometricGraph):
    """
    A class for representing proximity graphs.

    Proximity graphs, also known as neighborhood graphs, are geometric graphs
    where two vertices are connected if they are "close" to each other according
    to some proximity rule. The definition of "close" is what distinguishes
    different types of proximity graphs.

    This class serves as a base for various specific proximity graph
    implementations.

    Attributes
    ----------
    setpoints : SetPoints
        The set of points on which the graph is built.
    name : str
        The name of the graph, initialized to "Proximity Graph".

    """

    # CONSTRUCTOR

    def __init__(self, setpoints):
        """
        Initializes a ProximityGraph object.

        Parameters
        ----------
        setpoints : SetPoints
            An object containing the set of points.

        """
        GeometricGraph.__init__(self, setpoints)
        self.name = "Proximity Graph"

    @classmethod
    def from_graph(cls, geom_graph):
        """
        Creates a ProximityGraph from an existing GeometricGraph.

        This class method allows for the conversion of a generic geometric graph
        into a proximity graph, inheriting its points.

        Parameters
        ----------
        geom_graph : GeometricGraph
            The geometric graph to convert.

        Returns
        -------
        ProximityGraph
            A new ProximityGraph object.

        """
        setpoints = geom_graph.setpoints
        proximity_graph = cls(setpoints)
        proximity_graph._GeometricGraph__add_lengths()
        return proximity_graph

    # METHODS
    def __check_parameter(
        cls,
        parameter,
        range_min=None,
        range_max=None,
        strict=False,
        data_type=None,
    ):
        if data_type is None:
            data_type = [int, float, np.float64]
        if type(parameter) not in data_type:
            raise TypeError()
        inequality = cls.__closed_region(strict)
        strict_text = " or equal " if strict else " "
        if range_min is not None and inequality(parameter, range_min):
            raise ValueError(
                f"The parameter is less{strict_text}than " + str(range_min)
            )
        if range_max is not None and inequality(range_max, parameter):
            raise ValueError(
                f"The parameter is greater{strict_text}than " + str(range_max)
            )

    def __closed_region(cls, strict):
        if strict is True:

            def inequality(x, y):
                return x <= y
        else:

            def inequality(x, y):
                return x < y

        return inequality

    def __closed_region(cls, closed):
        """
        Returns an inequality function based on the 'closed' parameter.

        This method is used to define whether the proximity region is open or
        closed. A closed region includes its boundary (<=), while an open
        region does not (<).

        Parameters
        ----------
        closed : bool
            If True, the region is closed. If False, it's open.

        Returns
        -------
        function
            A lambda function representing either `<=` or `<`.

        """
        if closed is True:

            def inequality(x, y):
                return x <= y
        else:

            def inequality(x, y):
                return x < y

        return inequality
