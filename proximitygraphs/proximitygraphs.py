import numpy as np
from collections import Counter, defaultdict
from scipy.spatial import Delaunay
from scipy.spatial import ConvexHull
from scipy.spatial.distance import cdist, pdist
from itertools import combinations
from igraph import Graph
import warnings

from .points import SetPoints
from .geometricgraphs import GeometricGraph


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
        data_type=[int, float, np.float64],
    ):
        if type(parameter) not in data_type:
            raise TypeError()
        inequality = cls.__closed_region(strict)
        if strict:
            strict_text = " or equal "
        else:
            strict_text = " "
        if range_min is not None:
            if inequality(parameter, range_min):
                raise ValueError(
                    f"The parameter is less{strict_text}than " + str(range_min)
                )
        if range_max is not None:
            if inequality(range_max, parameter):
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


class Beta_Skeleton(ProximityGraph):
    # Atributos de clase
    matrix_r = np.array([[0, -1], [1, 0]])

    # CONSTRUCTOR
    def __init__(self, setpoints, beta=1.5, type_region="lune", closed=False):
        self._ProximityGraph__check_parameter(beta, range_min=0, strict=True)
        ProximityGraph.__init__(self, setpoints)
        self.name = "β-Skeleton"
        self.details = f"β={beta}, closed={closed}, type={type_region}"
        pairs = self.__defined_pairs(beta, type_region, closed)
        self.__assign_edges(pairs, beta, closed)
        self.graph.simplify()
        self._GeometricGraph__size()
        self._GeometricGraph__add_lengths()

    @classmethod
    def from_graph(cls, geom_graph, beta=1.5, type_region="lune", closed=False):
        skeleton = cls.__new__(cls)
        skeleton._ProximityGraph__check_parameter(beta, range_min=0, strict=True)
        skeleton.name = "β-Skeleton"
        skeleton.details = (
            f"β={beta}, closed={closed}, type={type_region}, (from graph)"
        )
        skeleton._GeometricGraph__setpoints = geom_graph.setpoints
        skeleton._GeometricGraph__graph = Graph()
        skeleton._GeometricGraph__graph.add_vertices(geom_graph.n)
        pairs = np.array(geom_graph.graph.get_edgelist())
        if beta < 1:
            if type_region != "intersection":
                warnings.warn(
                    f"For β<1, the region type {type_region} is undefined.\nUse type_region='intersection'instead."
                )
            skeleton.__empty_region = lambda p, q: skeleton.__intersection(p, q, beta)
            skeleton.__test = lambda test_1, test_2: test_1 * test_2
        elif beta >= 1:
            if type_region not in ["lune", "circle"]:
                raise TypeError("'type_region' must be 'lune' or 'circle' when β > 1.")
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
                    f"For β<1, the region type {type_region} is undefined.\nUse type_region='intersection'instead."
                )
            pairs = self.__pairs_by_combinations()
            self.__empty_region = lambda p, q: self.__intersection(p, q, beta)
            self.__test = lambda test_1, test_2: test_1 * test_2
        elif beta >= 1:
            if type_region not in ["lune", "circle"]:
                raise TypeError("'type_region' must be 'lune' or 'circle' when β > 1.")
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


class RNG(Beta_Skeleton):
    # CONSTRUCTOR
    def __init__(self, setpoints, closed=False):
        Beta_Skeleton.__init__(self, setpoints, beta=2, closed=closed)
        self.name = "Relative Neighborhood Graph"
        self.details = f"closed={closed}"


class GG(Beta_Skeleton):
    # CONSTRUCTOR
    def __init__(self, setpoints, closed=True):
        Beta_Skeleton.__init__(self, setpoints, beta=1, closed=closed)
        self.name = "Gabriel Graph"
        self.details = f"closed={closed}"


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


class Sigma_Graph(ProximityGraph):
    """
    Constructs a σ-Graph.

    The σ-Graph is a proximity graph where an edge connects two points p and q
    if the two open disks of radius dist(p, q) / σ centered at p and q are
    empty of other points. The parameter σ >= 1 controls the size of these
    disks.

    - The edge (p, q) is in the graph if for all other points z:
        dist(p, z) > dist(p, q) / σ
        dist(q, z) > dist(p, q) / σ

    - When σ = 1, the condition is that the open disks centered at p and q with
      radius dist(p, q) must be empty.
    - As σ increases, the radius of the disks decreases, leading to more edges.

    Attributes
    ----------
    name : str
        The name of the graph, set to "σ-Graph".
    details : str
        Additional details, including the value of σ and whether the region is
        closed.

    """

    # CONSTRUCTOR

    def __init__(self, setpoints, sigma=1, closed=False):
        """
        Initializes a Sigma_Graph object.

        Parameters
        ----------
        setpoints : SetPoints
            An object containing the set of points.
        sigma : int or float, optional
            The parameter controlling the size of the empty disks (default is 1).
            Must be >= 1.
        closed : bool, optional
            Whether the empty region is closed (>=) or open (>) (default is False).

        """
        if not isinstance(sigma, (int, float)):
            raise TypeError("sigma must be a number.")
        if sigma < 1:
            raise ValueError("sigma must be greater than or equal to 1.")
        if not isinstance(closed, bool):
            raise TypeError("closed must be a boolean.")

        ProximityGraph.__init__(self, setpoints)
        self.name = "σ-Graph"
        self.details = "σ=" + str(sigma) + ", closed=" + str(closed)
        self.inequality = self._ProximityGraph__closed_region(closed)
        self.__assign_edges(sigma)
        self.graph.simplify()
        self._GeometricGraph__size()
        self._GeometricGraph__add_lengths()

    def __assign_edges(self, sigma):
        """
        Tests pairs of points and adds edges based on the σ-Graph criterion.

        Parameters
        ----------
        sigma : int or float
            The σ parameter for the graph.

        """
        if self.n < 2:
            return
        pairs = combinations(range(self.n), 2)
        edges = []

        if self.n <= self._GeometricGraph__limit_vec:
            pairs = np.array(list(pairs))
            p = self.points[pairs[:, 0]]
            q = self.points[pairs[:, 1]]
            dist_sigma = pdist(self.points) / sigma
            for i in np.arange(pairs.shape[0]):
                # Check empty disk around p
                dist_1 = np.linalg.norm(self.points - p[i], axis=1)
                empty_test_1 = self.inequality(dist_1, dist_sigma[i])
                empty_test_1 = np.delete(empty_test_1, pairs[i])
                if not np.any(empty_test_1):
                    # Check empty disk around q
                    dist_2 = np.linalg.norm(self.points - q[i], axis=1)
                    empty_test_2 = self.inequality(dist_2, dist_sigma[i])
                    empty_test_2 = np.delete(empty_test_2, pairs[i])
                    if not np.any(empty_test_2):
                        edges.append(pairs[i])
        else:  # Iterative approach for larger datasets
            for pair in pairs:
                p = self.points[pair[0]]
                q = self.points[pair[1]]
                dist_sigma = np.linalg.norm(p - q) / sigma
                # Check empty disk around p
                dist_1 = np.linalg.norm(self.points - p, axis=1)
                empty_test_1 = self.inequality(dist_1, dist_sigma)
                empty_test_1 = np.delete(empty_test_1, pair)
                if not np.any(empty_test_1):
                    # Check empty disk around q
                    dist_2 = np.linalg.norm(self.points - q, axis=1)
                    empty_test_2 = self.inequality(dist_2, dist_sigma)
                    empty_test_2 = np.delete(empty_test_2, pair)
                    if not np.any(empty_test_2):
                        edges.append((pair[0], pair[1]))
        self._GeometricGraph__graph.add_edges(edges)


class Unit_Disk(ProximityGraph):
    """
    Constructs a Unit Disk Graph.

    A Unit Disk Graph is a model where nodes are points in the plane, and an
    edge exists between two points if their Euclidean distance is less than or
    equal to a certain maximum distance, `dist_max`. This `dist_max` can be
    thought of as the "unit" distance.

    This type of graph is commonly used in wireless network modeling, where
    nodes represent devices and `dist_max` represents the communication range.

    Attributes
    ----------
    name : str
        The name of the graph, set to "Unit Disk Graph".
    details : str
        Additional details, including the maximum distance and whether the
        distance condition is inclusive.

    """

    # CONSTRUCTOR

    def __init__(self, setpoints, dist_max, closed=True):
        """
        Initializes a Unit_Disk object.

        Parameters
        ----------
        setpoints : SetPoints
            An object containing the set of points.
        dist_max : int or float
            The maximum distance for two points to be connected.
        closed : bool, optional
            If True (default), the distance condition is `<= dist_max`.
            If False, it is `< dist_max`.

        """
        if not isinstance(dist_max, (int, float)):
            raise TypeError("dist_max must be a number.")
        if dist_max < 0:
            raise ValueError("dist_max must be a non-negative number.")
        if not isinstance(closed, bool):
            raise TypeError("closed must be a boolean.")

        ProximityGraph.__init__(self, setpoints)
        self.name = "Unit Disk Graph"
        self.details = "distance max=" + str(dist_max) + ", closed=" + str(closed)
        self.inequality = self._ProximityGraph__closed_region(closed)
        self.__assign_edges(dist_max)
        self.graph.simplify()
        self._GeometricGraph__size()
        self._GeometricGraph__add_lengths()

    def __assign_edges(self, dist_max):
        """
        Connects all pairs of points whose distance is within `dist_max`.

        Parameters
        ----------
        dist_max : int or float
            The maximum distance threshold.

        """
        # Vectorized approach for smaller datasets
        if self.n <= self._GeometricGraph__limit_vec:
            pairs = list(combinations(range(self.n), 2))
            if not pairs:
                return
            pairs = np.array(pairs)
            dist_pairs = pdist(self.points)
            dist_disk = self.inequality(dist_pairs, dist_max)
            edges = pairs[dist_disk]
        else:  # Iterative approach for larger datasets
            edges = []
            for i in range(self.n):
                # Calculate distance from point i to all other points
                dist = np.linalg.norm(self.points - self.points[i], axis=1)
                # Find indices of points within the distance
                neighbors = np.where(self.inequality(dist, dist_max))[0]
                # Create edges, avoiding self-loops and duplicates
                for j in neighbors:
                    if i < j:
                        edges.append((i, j))
        self._GeometricGraph__graph.add_edges(edges)


class SIG(ProximityGraph):
    """
    Constructs the Sphere of Influence Graph (SIG).

    The SIG is defined on a set of points in a metric space. For each point p,
    consider an open ball (or "sphere of influence") centered at p with radius
    equal to the distance to its nearest neighbor. An edge exists between two
    points p and q if their spheres of influence intersect.

    Mathematically, an edge (p, q) is in the SIG if:
        dist(p, q) <= radius(p) + radius(q)
    where radius(p) is the distance from p to its nearest neighbor.

    The SIG is related to the concept of territoriality and is used in various
    fields, including pattern recognition and spatial analysis.

    Attributes
    ----------
    name : str
        The name of the graph, set to "Sphere Influence Graph".
    details : str
        Additional details, including whether the intersection condition is
        inclusive.

    """

    # CONSTRUCTOR

    def __init__(self, setpoints, closed=False):
        """
        Initializes a SIG object.

        Parameters
        ----------
        setpoints : SetPoints
            An object containing the set of points.
        closed : bool, optional
            If False (default), the intersection is based on open balls (<).
            If True, it is based on closed balls (<=).

        """
        ProximityGraph.__init__(self, setpoints)
        if not isinstance(closed, bool):
            raise TypeError("closed must be a boolean.")
        self.name = "Sphere Influence Graph"
        self.details = "closed=" + str(closed)
        self.inequality = self._ProximityGraph__closed_region(closed)
        self.__assign_edges()
        self.graph.simplify()
        self._GeometricGraph__size()
        self._GeometricGraph__add_lengths()

    def __assign_edges(self):
        """
        Connects pairs of points whose spheres of influence intersect.

        This method first computes the nearest neighbor distance for each point,
        which defines the radius of its sphere of influence. Then, it checks
        all pairs of points for intersection.

        """
        if self.n < 2:
            return
        pairs = combinations(range(self.n), 2)
        # Get the radius for each point's sphere of influence
        dist_min = self._GeometricGraph__dist_nearest()

        # Vectorized approach for smaller datasets
        if self.n <= self._GeometricGraph__limit_vec:
            pairs = np.array(list(pairs))

            def dist_min_sum(p, q):
                return dist_min[p] + dist_min[q]

            dist_min_sum_vec = np.vectorize(dist_min_sum)
            # Check if distance between pairs is less than sum of radii
            influence = self.inequality(
                pdist(self.points), dist_min_sum_vec(pairs[:, 0], pairs[:, 1])
            )
            edges = pairs[influence]
        else:  # Iterative approach for larger datasets
            edges = []
            for p, q in pairs:
                dist = np.linalg.norm(self.points[p] - self.points[q])
                if self.inequality(dist, dist_min[p] + dist_min[q]):
                    edges.append((p, q))
        self.graph.add_edges(edges)


class Elliptic_GabrielG(ProximityGraph):
    """
    Constructs the Elliptic Gabriel Graph (EGG) of a set of points.

    Two points p and q are connected if the ellipse with foci at p and q and
    major axis length α * ||p - q|| contains no other points.

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
        self.details = "α=" + str(alpha)
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
        egg.details = "α=" + str(alpha)
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


class Alpha_Shape(ProximityGraph):
    """
    Constructs the α-Shape boundary of a planar point set.

    Two vertices i and j are connected iff edge (i, j) lies on the
    boundary of triangles whose circumradius R satisfies
    ``R <= 1/|α| + tol``. For ``α ≈ 0`` the boundary reduces to the
    convex hull. For ``α > 0`` the furthest-site Delaunay variant is used.

    Attributes
    ----------
    name : str
        Graph name, set to ``"Alpha-Shape"``.
    details : str
        Short descriptor with the chosen α, e.g., ``"alpha=2.0"``.
    graph : GeometricGraph
        Underlying geometric graph populated with boundary edges.
    points : ndarray of shape (n, 2)
        Input coordinates as provided by the base class.
    n : int
        Number of input points.
    """

    def __init__(
        self,
        setpoints,
        alpha: float,
        tol: float = 1e-12,
        qhull_options: str | None = None,
    ):
        """
        Initializes an Alpha_Shape object and builds the boundary.

        Parameters
        ----------
        setpoints : SetPoints
            Container holding the input coordinates. Must expose
            ``points`` (ndarray of shape (n, 2)) and the interfaces
            expected by ``ProximityGraph``.
        alpha : float
            Alpha parameter controlling the radius cutoff via
            ``R_alpha = 1 / |alpha|``. Values near zero approach the
            convex hull.
        tol : float, optional
            Nonnegative tolerance added to the radius inequality,
            default ``1e-12``.
        qhull_options : str or None, optional
            Options string forwarded to ``scipy.spatial.Delaunay`` /
            Qhull. Default ``None``.

        Notes
        -----
        Cases:
          * ``n <= 1``: no edges.
          * ``n == 2`` and ``α ≈ 0``: single edge.
          * ``α ≈ 0`` and ``n >= 3``: convex hull edges.
          * Else: Delaunay filtering by circumradius, then keep edges
            with multiplicity one (boundary of the kept triangles).

        See Also
        --------
        scipy.spatial.Delaunay
        scipy.spatial.ConvexHull
        """
        ProximityGraph.__init__(self, setpoints)
        self.name = "Alpha-Shape"
        self.details = f"alpha={alpha}"
        self._qhull_options = qhull_options

        pts = self.points
        n = self.n
        edges_to_add = []

        if n == 0:
            pass
        elif n == 1:
            pass
        elif n == 2:
            if np.isclose(alpha, 0.0):
                edges_to_add = [(0, 1)]
        else:
            if np.isclose(alpha, 0.0):
                hull = ConvexHull(pts)
                edges_to_add = list(map(tuple, hull.simplices))
            else:
                furthest = bool(alpha > 0)
                tris = Delaunay(
                    pts,
                    furthest_site=furthest,
                    incremental=False,
                    qhull_options=qhull_options,
                ).simplices
                if tris.size > 0:
                    R = self._batch_circumradius(pts, tris)
                    R_alpha = 1.0 / abs(alpha)
                    keep = R <= (R_alpha + tol)
                    kept = tris[keep]
                    if kept.size > 0:
                        all_edges = self._edges_from_triangles(kept)
                        counts = Counter(all_edges)
                        edges_to_add = [e for e, c in counts.items() if c == 1]
        # Add edges and finalize
        if edges_to_add:
            self.graph.add_edges(edges_to_add)
            self.graph.simplify()  # simplify is in case of duplicates

        self._GeometricGraph__size()
        self._GeometricGraph__add_lengths()

    # ---------- helpers ----------
    @staticmethod
    def _batch_circumradius(
        points: np.ndarray, triangles_idx: np.ndarray
    ) -> np.ndarray:
        """
        Computes triangle circumradii in batch.

        Parameters
        ----------
        points : ndarray of shape (n, 2)
            Planar coordinates.
        triangles_idx : ndarray of shape (m, 3)
            Vertex indices of the triangles.

        Returns
        -------
        ndarray of shape (m,)
            Circumradius per triangle. Degenerates get ``np.inf``.

        Notes
        -----
        Uses twice the signed area from the shoelace formula and
        ``R = abc/(4A)`` implemented as
        ``(a*b*c)/(2*|shoelace|) / 2``.
        """
        if len(triangles_idx) == 0:
            return np.empty((0,), dtype=float)
        A = points[triangles_idx[:, 0]]
        B = points[triangles_idx[:, 1]]
        C = points[triangles_idx[:, 2]]
        shoelace = (B[:, 0] - A[:, 0]) * (C[:, 1] - A[:, 1]) - (B[:, 1] - A[:, 1]) * (
            C[:, 0] - A[:, 0]
        )
        twice_area = np.abs(shoelace)
        a = np.linalg.norm(B - C, axis=1)
        b = np.linalg.norm(A - C, axis=1)
        c = np.linalg.norm(A - B, axis=1)
        with np.errstate(divide="ignore", invalid="ignore"):
            circum_radius = (a * b * c) / twice_area
        circum_radius[twice_area == 0.0] = np.inf
        return circum_radius / 2.0

    @staticmethod
    def _edges_from_triangles(triangles_idx: np.ndarray):
        """
        Generates undirected edges from triangle connectivity.

        Parameters
        ----------
        triangles_idx : ndarray of shape (m, 3)
            Vertex indices of the triangles.

        Returns
        -------
        list of tuple of int
            Edge list as sorted pairs ``(i, j)``. Multiplicities are
            preserved; deduplication is not performed.
        """
        e = np.vstack(
            [
                triangles_idx[:, [0, 1]],
                triangles_idx[:, [1, 2]],
                triangles_idx[:, [2, 0]],
            ]
        )
        e.sort(axis=1)
        return [tuple(row) for row in e]

    @staticmethod
    def _boundary_cycles_2regular(boundary_edges):
        """
        Extracts cycles from a 2-regular boundary.

        Assumes every boundary vertex has degree 2 and traverses each
        connected component as a simple cycle.

        Parameters
        ----------
        boundary_edges : iterable of tuple of int
            Sorted undirected edges ``(i, j)``, ``i != j``.

        Returns
        -------
        list of list of int
            Cycles as ordered vertex index sequences, length ≥ 3.
            The start vertex is not repeated at the end.

        Notes
        -----
        Linear in the number of boundary edges. Intended for
        post-processing and diagnostics.
        """
        neighbors = defaultdict(list)
        E = set()
        for i, j in boundary_edges:
            u, v = (i, j) if i < j else (j, i)
            neighbors[u].append(v)
            neighbors[v].append(u)
            E.add((u, v))
        cycles = []
        while E:
            u, v = next(iter(E))
            start, prev, curr = u, u, v
            cycle = [start, curr]
            E.discard((min(prev, curr), max(prev, curr)))
            while True:
                nxt = None
                for w in neighbors[curr]:
                    e = (min(curr, w), max(curr, w))
                    if w != prev and e in E:
                        nxt = w
                        break
                if nxt is None:
                    break
                cycle.append(nxt)
                E.discard((min(curr, nxt), max(curr, nxt)))
                prev, curr = curr, nxt
                if curr == start:
                    break
            if len(cycle) >= 3 and cycle[0] == cycle[-1]:
                cycle = cycle[:-1]
            if len(cycle) >= 3:
                cycles.append(cycle)
        return cycles


class Alpha_Hull(ProximityGraph):
    """
    Constructs the α-Hull of a planar point set.

    For ``α ≈ 0`` the object reduces to the convex hull rendered as straight
    segments. For ``α ≠ 0`` it reuses the α-shape boundary and replaces each
    boundary edge by a circular arc of radius ``R = 1/|α|`` consistent with the
    interior/exterior choice implied by ``sign(α)`` and the boundary orientation.
    The geometric graph stores straight segments for analytics, while sampled
    arc points are kept in ``self.arcs`` for rendering.

    Attributes
    ----------
    name : str
        Graph name, set to ``"Alpha-Hull"``.
    details : str
        Short descriptor with α, e.g., ``"alpha=1.5"``.
    arcs : list of (n_i, 2) ndarray
        Sampled points of each circular arc for plotting.
    segments : list of tuple of int
        Straight segments used in the analytics graph (one per boundary edge).
    graph : GeometricGraph
        Underlying graph populated with ``segments``.
    points : ndarray of shape (n, 2)
        Input coordinates as provided by the base class.
    n : int
        Number of input points.

    Notes
    -----
    Pipeline:
      1) If ``α ≈ 0`` use convex hull edges.
      2) Else build ``Alpha_Shape`` with the same ``α`` to get boundary cycles.
      3) For each boundary edge ``(p, q)`` compute candidate circle centers of
         radius ``R = 1/|α|`` through ``p`` and ``q``.
      4) Select the center whose arc is interior if ``α > 0`` and exterior if
         ``α < 0``, based on polygon signed area and local orientation tests.
      5) Sample the minor arc between ``p`` and ``q`` and store in ``arcs``.
      6) Insert ``(i, j)`` as a straight edge into ``graph`` for analytics.

    See Also
    --------
    Alpha_Shape : Boundary extractor used to seed α-Hull construction.
    scipy.spatial.ConvexHull : Hull used when ``α ≈ 0``.
    """

    def __init__(
        self,
        setpoints,
        alpha: float,
        n_points_per_arc: int = 40,
        tol: float = 1e-12,
        qhull_options: str | None = None,
    ):
        """
        Initializes an Alpha_Hull object and builds the hull representation.

        Parameters
        ----------
        setpoints : SetPoints
            Container with ``points`` (ndarray of shape (n, 2)) and interfaces
            expected by ``ProximityGraph``.
        alpha : float
            α parameter. For ``α ≈ 0`` the convex hull is used. For ``α ≠ 0``
            the circular-arc hull uses radius ``R = 1/|α|``.
        n_points_per_arc : int, optional
            Number of samples along each minor arc between its endpoints.
            Default is 40.
        tol : float, optional
            Tolerance forwarded to the internal α-shape filtering. Default 1e-12.
        qhull_options : str or None, optional
            Options string forwarded to the Delaunay builder used by
            ``Alpha_Shape``. Default ``None``.
        """
        ProximityGraph.__init__(self, setpoints)
        self.name = "Alpha-Hull"
        self.details = f"alpha={alpha}"
        self.arcs = []  # list[np.ndarray] of sampled arc points
        self.segments = []  # list[tuple[int,int]] fallback straight segments
        pts = self.points
        n = self.n

        if n < 2:
            self._GeometricGraph__size()
            self._GeometricGraph__add_lengths()
            return
        if np.isclose(alpha, 0.0):
            # convex hull as straight segments
            hull = ConvexHull(pts)
            cyc = list(hull.vertices)
            k = len(cyc)
            self.segments = [(cyc[t], cyc[(t + 1) % k]) for t in range(k)]
        else:
            # reuse α-shape boundary cycles
            shape = Alpha_Shape(setpoints, alpha, tol=tol, qhull_options=qhull_options)
            bedges = shape.graph.get_edgelist()
            cycles = Alpha_Shape._boundary_cycles_2regular(bedges)
            R = 1.0 / abs(alpha)
            for cyc in cycles:
                k = len(cyc)
                # orientation for center choice
                area = self._polygon_signed_area(pts[np.asarray(cyc)])
                for t in range(k):
                    i, j = cyc[t], cyc[(t + 1) % k]
                    p, q = pts[i], pts[j]
                    centers = self._circle_centers_through_pair(p, q, R)
                    if not centers:
                        self.segments.append((i, j))
                        continue
                    e = q - p
                    s0 = e[0] * (centers[0][1] - p[1]) - e[1] * (centers[0][0] - p[0])
                    s1 = e[0] * (centers[1][1] - p[1]) - e[1] * (centers[1][0] - p[0])
                    if alpha < 0:  # exterior
                        chosen = (
                            centers[0]
                            if (area > 0 and s0 < s1) or (area < 0 and s0 > s1)
                            else centers[1]
                        )
                    else:  # interior
                        chosen = (
                            centers[0]
                            if (area > 0 and s0 > s1) or (area < 0 and s0 < s1)
                            else centers[1]
                        )
                    arc_pts = self._arc_points_minor(
                        chosen, R, p, q, n_points=n_points_per_arc
                    )
                    self.arcs.append(arc_pts)
                    # keep straight edge in graph for analytics
                    self.segments.append((i, j))

        if self.segments:
            self.graph.add_edges(self.segments)
            self.graph.simplify()
        self._GeometricGraph__size()
        self._GeometricGraph__add_lengths()

    # ---------- custom drawing overriding igraph to render arcs ----------
    def draw(
        self,
        figsize=(6, 6),
        v_size=3,
        v_color="#00072D",
        v_alpha=1,
        e_size=1,
        e_color="#0A2472",
        e_alpha=1,
        title=True,
        fontsize=10,
        details=False,
        axis=False,
        save=None,
        *,
        fig_kwargs=None,
        v_kwargs=None,
        e_kwargs=None,
        title_kwargs=None,
        savefig_kwargs=None,
    ):
        """
        Plots the α-Hull with circular arcs.

        Parameters
        ----------
        figsize : tuple of (float, float), optional
            Figure size in inches. Default (6, 6).
        v_size : float, optional
            Marker size for vertices. 0 disables vertex scatter. Default 3.
        v_color : str, optional
            Vertex color passed to Matplotlib. Default "#00072D".
        v_alpha : float, optional
            Vertex alpha (transparency) level between 0 (transparent) and 1 (opaque). Default 1.
        e_size : float, optional
            Line width for arcs. Default 1.
        e_color : str, optional
            Color for arcs. Default "#0A2472".
        e_alpha : float, optional
            Arc alpha (transparency) level between 0 (transparent) and 1 (opaque). Default 1.
        title : bool, optional
            Whether to set a title. Default True.
        fontsize : float, optional
            Title font size. Default 10.
        details : bool, optional
            If True, appends self.details to the title (if present). Default False.
        axis : bool, optional
            If True, show axes. Default False.
        save : str or None, optional
            If set, saves a ".png" at save + ".png".
            If None, returns the live figure and axes.

        Other Parameters
        ----------------
        fig_kwargs : dict, optional
            Extra keyword arguments passed to matplotlib.pyplot.subplots.
        v_kwargs : dict, optional
            Extra keyword arguments passed to ax.scatter (vertex scatter).
            These override v_size, v_color, v_alpha if duplicated.
        e_kwargs : dict, optional
            Extra keyword arguments passed to ax.plot (arcs).
            These override e_size, e_color, e_alpha if duplicated.
        title_kwargs : dict, optional
            Extra keyword arguments passed to ax.set_title.
            These override fontsize if duplicated.
        savefig_kwargs : dict, optional
            Extra keyword arguments passed to matplotlib.pyplot.savefig.

        Returns
        -------
        (fig, ax) : tuple
            Matplotlib figure and axes.
        """
        fig_kwargs = {} if fig_kwargs is None else dict(fig_kwargs)
        v_kwargs = {} if v_kwargs is None else dict(v_kwargs)
        e_kwargs = {} if e_kwargs is None else dict(e_kwargs)
        title_kwargs = {} if title_kwargs is None else dict(title_kwargs)
        savefig_kwargs = {} if savefig_kwargs is None else dict(savefig_kwargs)

        # figure and axes
        from matplotlib.pyplot import gcf, subplots

        fig, ax = subplots(figsize=figsize, **fig_kwargs)

        # vertices
        if getattr(self, "n", 0) > 0 and v_size > 0:
            scatter_kwargs = dict(s=v_size, c=v_color, alpha=v_alpha)
            scatter_kwargs.update(v_kwargs)  # user overrides defaults
            ax.scatter(self.points[:, 0], self.points[:, 1], **scatter_kwargs)

        # arcs (same "edges" slot, but drawn as curves)
        arcs = getattr(self, "arcs", None)
        if arcs:
            line_kwargs = dict(linewidth=e_size, color=e_color, alpha=e_alpha)
            line_kwargs.update(e_kwargs)  # user overrides defaults
            for arc in arcs:
                # arc expected shape (m, 2)
                ax.plot(arc[:, 0], arc[:, 1], **line_kwargs)

        # title
        if title:
            plot_title = getattr(self, "name", self.__class__.__name__)
            if details and getattr(self, "details", None):
                plot_title += f"\n{self.details}"
            title_args = dict(fontsize=fontsize)
            title_args.update(title_kwargs)
            ax.set_title(plot_title, **title_args)

        # axes
        if not axis:
            ax.set_axis_off()
        else:
            ax.set_axis_on()
        ax.set_aspect("equal", adjustable="box")

        # save or return
        if save is None:
            return fig, ax
        else:

            def savefig(*args, **kwargs) -> None:
                fig = gcf()
                # savefig default implementation has no return, so mypy is unhappy
                # presumably this is here because subclasses can return?
                # type: ignore[func-returns-value]
                res = fig.savefig(*args, **kwargs)
                # Need this if 'transparent=True', to reset colors.
                fig.canvas.draw_idle()
                return res

            savefig(save + ".png", bbox_inches="tight", **savefig_kwargs)
            return fig, ax

    # ---------- helpers ----------

    @staticmethod
    def _polygon_signed_area(xy: np.ndarray) -> float:
        """
        Signed area of a polygonal cycle.

        Parameters
        ----------
        xy : ndarray of shape (k, 2)
            Ordered polygon vertices.

        Returns
        -------
        float
            Positive for counter-clockwise orientation, negative for clockwise.

        Notes
        -----
        Implements the shoelace formula:
        ``A = 0.5 * sum(x_i y_{i+1} - y_i x_{i+1})`` with cyclic indexing.

        """
        x, y = xy[:, 0], xy[:, 1]
        return 0.5 * np.sum(x * np.roll(y, -1) - y * np.roll(x, -1))

    @staticmethod
    def _circle_centers_through_pair(
        p: np.ndarray,
        q: np.ndarray,
        radius: float,
        eps: float = 1e-12,
    ):
        """
        Circle centers of radius ``radius`` passing through points ``p`` and ``q``.

        Parameters
        ----------
        p, q : ndarray of shape (2,)
            Endpoints of the chord.
        radius : float
            Circle radius ``R``. Must satisfy ``||p - q|| <= 2R``.
        eps : float, optional
            Tolerance for degeneracy checks on the chord length. Default 1e-12.

        Returns
        -------
        list of ndarray
            Either two centers, one center in the tangent case, or an empty list
            if no circle of radius ``R`` passes through ``p`` and ``q``.

        """
        pq = q - p
        d = np.linalg.norm(pq)
        if d < eps or d > 2 * radius + 1e-9:
            return []
        mid = 0.5 * (p + q)
        u = pq / d
        n_perp = np.array([-u[1], u[0]])
        h = np.sqrt(max(0.0, radius * radius - (d * d) / 4.0))
        return [mid + h * n_perp, mid - h * n_perp]

    @staticmethod
    def _arc_points_minor(
        center: np.ndarray,
        radius: float,
        p: np.ndarray,
        q: np.ndarray,
        n_points: int = 40,
    ):
        """
        Sampled points along the minor arc from ``p`` to ``q``.

        Parameters
        ----------
        center : ndarray of shape (2,)
            Circle center.
        radius : float
            Circle radius.
        p, q : ndarray of shape (2,)
            Arc endpoints on the circle.
        n_points : int, optional
            Number of samples along the minor arc, inclusive of endpoints
            if you append them externally. Default 40.

        Returns
        -------
        ndarray of shape (n_points, 2)
            Sampled arc coordinates.

        Notes
        -----
        Uses angle unwrapping to ensure the minor-arc sweep with
        ``Δθ ∈ (-π, π]``.

        """
        cp = p - center
        cq = q - center
        th1 = np.arctan2(cp[1], cp[0])
        th2 = np.arctan2(cq[1], cq[0])
        dtheta = (th2 - th1 + np.pi) % (2 * np.pi) - np.pi
        thetas = th1 + np.linspace(0.0, 1.0, n_points) * dtheta
        return center + np.column_stack([np.cos(thetas), np.sin(thetas)]) * radius


class Gamma_Graph(ProximityGraph):
    """
    Constructs the γ-Neighborhood Graph (y-Graph) as defined by Veltkamp (1992).

    Two points p and q are connected if at least one γ-neighborhood
    N_{γ0,γ1}(p, q) is empty of all other sites.

    Parameters
    ----------
    setpoints : SetPoints
        The set of points.
    gamma0 : float
        First γ parameter, in [-1, 1].
    gamma1 : float
        Second γ parameter, in [-1, 1], with |gamma0| <= |gamma1|.
    closed : bool, optional
        If False (default), emptiness is with strict "<" (open region).
        If True, emptiness uses "<=" (closed region).
    block_size : int, optional
        Number of candidate pairs to process per vectorized block in the
        finite-radius case. Larger => faster but more memory.
    """

    # CONSTRUCTOR
    def __init__(self, setpoints, gamma0=0.0, gamma1=0.0, closed=False, block_size=512):

        # Allow -1 <= gamma <= 1 for the special cases in Veltkamp
        self._ProximityGraph__check_parameter(gamma0, range_min=-1, strict=False)
        self._ProximityGraph__check_parameter(gamma0, range_max=1, strict=False)
        self._ProximityGraph__check_parameter(gamma1, range_min=-1, strict=False)
        self._ProximityGraph__check_parameter(gamma1, range_max=1, strict=False)

        if abs(gamma0) > abs(gamma1):
            raise ValueError("|gamma0| must be less than or equal to |gamma1|.")
        if not isinstance(closed, bool):
            raise TypeError("closed must be a boolean.")
        if type(block_size) not in [int, np.int64] or block_size <= 0:
            raise ValueError("block_size must be a positive integer.")

        ProximityGraph.__init__(self, setpoints)
        self.name = "γ-Neighborhood Graph"
        self.details = f"γ0={gamma0}, γ1={gamma1}, closed={closed}"
        self.__gamma0 = float(gamma0)
        self.__gamma1 = float(gamma1)
        self.__inequality = self._ProximityGraph__closed_region(closed)
        self.__block_size = int(block_size)

        g0 = self.__gamma0
        g1 = self.__gamma1

        # ---- Special half-plane limit cases (k = 2) ----
        if g0 == 1.0 and g1 == 1.0:
            # y(1,1): void graph
            self.graph.simplify()
            self._GeometricGraph__size()
            self._GeometricGraph__add_lengths()
            return

        if g0 == -1.0 and g1 == -1.0:
            # y(-1,-1): complete graph (general position)
            pairs = np.array(list(combinations(range(self.n), 2)), dtype=int)
            if pairs.size > 0:
                self.graph.add_edges(list(map(tuple, pairs)))
            self.graph.simplify()
            self._GeometricGraph__size()
            self._GeometricGraph__add_lengths()
            return

        if (g0 == -1.0 and g1 == 1.0) or (g0 == 1.0 and g1 == -1.0):
            # y(-1,1) and y(1,-1): convex hull graph
            hull = Convex_Hull(self.setpoints)
            edges = hull.graph.get_edgelist()
            if edges:
                self.graph.add_edges(edges)
            self.graph.simplify()
            self._GeometricGraph__size()
            self._GeometricGraph__add_lengths()
            return

        # ---- Generic finite-radius case (no |γ| = 1) ----
        pairs = self.__defined_pairs()
        self.__assign_edges(pairs)  # uses self.__block_size

        self.graph.simplify()
        self._GeometricGraph__size()
        self._GeometricGraph__add_lengths()

    @classmethod
    def from_graph(
        cls, geom_graph, gamma0=0.0, gamma1=0.0, closed=False, block_size=512
    ):
        """
        Build a γ-Neighborhood Graph on top of an existing GeometricGraph.

        Parameters
        ----------
        geom_graph : GeometricGraph
            Base graph providing vertices. For the generic finite-radius
            case its edges are used as candidates.
        gamma0, gamma1, closed : see __init__.
        block_size : int, optional
            Vectorization block size (see __init__).
        """
        g = cls.__new__(cls)

        # It is neccessary to re-check parameters because __new__ bypasses __init__
        g._ProximityGraph__check_parameter(gamma0, range_min=-1, strict=False)
        g._ProximityGraph__check_parameter(gamma0, range_max=1, strict=False)
        g._ProximityGraph__check_parameter(gamma1, range_min=-1, strict=False)
        g._ProximityGraph__check_parameter(gamma1, range_max=1, strict=False)

        if abs(gamma0) > abs(gamma1):
            raise ValueError("|gamma0| must be less than or equal to |gamma1|.")
        if not isinstance(closed, bool):
            raise TypeError("closed must be a boolean.")
        if type(block_size) not in [int, np.int64] or block_size <= 0:
            raise ValueError("block_size must be a positive integer.")

        g.name = "γ-Neighborhood Graph"
        g.details = f"γ0={gamma0}, γ1={gamma1}, closed={closed}, (from graph)"
        g._GeometricGraph__setpoints = geom_graph.setpoints
        g._GeometricGraph__graph = Graph()
        g._GeometricGraph__graph.add_vertices(geom_graph.n)

        g.__gamma0 = float(gamma0)
        g.__gamma1 = float(gamma1)
        g.__inequality = g._ProximityGraph__closed_region(closed)
        g.__block_size = int(block_size)

        g0 = g.__gamma0
        g1 = g.__gamma1

        # Same special cases as in __init__
        if g0 == 1.0 and g1 == 1.0:
            g.graph.simplify()
            g._GeometricGraph__size()
            g._GeometricGraph__add_lengths()
            return g

        if g0 == -1.0 and g1 == -1.0:
            pairs = np.array(list(combinations(range(g.n), 2)), dtype=int)
            if pairs.size > 0:
                g.graph.add_edges(list(map(tuple, pairs)))
            g.graph.simplify()
            g._GeometricGraph__size()
            g._GeometricGraph__add_lengths()
            return g

        if (g0 == -1.0 and g1 == 1.0) or (g0 == 1.0 and g1 == -1.0):
            hull = Convex_Hull(geom_graph.setpoints)
            edges = hull.graph.get_edgelist()
            if edges:
                g.graph.add_edges(edges)
            g.graph.simplify()
            g._GeometricGraph__size()
            g._GeometricGraph__add_lengths()
            return g

        # Generic finite-radius case: use the base graph's edges as candidates
        candidate_pairs = np.array(geom_graph.graph.get_edgelist(), dtype=int)
        g.__assign_edges(candidate_pairs)  # uses g.__block_size

        g.graph.simplify()
        g._GeometricGraph__size()
        g._GeometricGraph__add_lengths()
        return g

    # ----- Internal helpers -----

    def __defined_pairs(self):
        """
        Candidate edges for the finite-radius case.

        Safe pruning:
        - If |gamma|=1 or gamma1<0 we cannot guarantee DT supersets -> all pairs.
        - Otherwise (finite radii, gamma1>=0) the γ-graph is a DT subgraph -> use DT edges.
        """
        g0, g1 = self.__gamma0, self.__gamma1
        dim = self.points.shape[1]

        # special/unsafe ranges -> all pairs
        if abs(g0) == 1.0 or abs(g1) == 1.0 or g1 < 0.0:
            return np.array(list(combinations(range(self.n), 2)), dtype=int)

        # not enough points for DT
        if self.n < dim + 1:
            return np.array(list(combinations(range(self.n), 2)), dtype=int)

        # DT candidates
        g_dt = DelaunayG(self.setpoints)
        return np.array(g_dt.graph.get_edgelist(), dtype=int)

    def __assign_edges(self, pairs):
        """
        Vectorized emptiness test in blocks.

        Parameters
        ----------
        pairs : (m,2) int ndarray
            Candidate pairs.
        """
        block_size = self.__block_size

        if self.n < 2 or pairs.size == 0:
            return

        pts = self.points  # (n,2)
        pts_norm2 = np.einsum("ij,ij->i", pts, pts)  # ||x||^2, (n,)

        g0, g1 = self.__gamma0, self.__gamma1

        # open vs closed comparison on squared distances
        closed = self.__inequality(0.0, 0.0)  # True iff <= is used
        if closed:

            def comp(dist2, R2):
                return dist2 <= R2
        else:

            def comp(dist2, R2):
                return dist2 < R2

        intersection_mode = g1 <= 0.0
        edges_out = []

        m_pairs = pairs.shape[0]
        for start in range(0, m_pairs, block_size):
            blk = pairs[start : start + block_size]
            if blk.size == 0:
                continue

            i = blk[:, 0]
            j = blk[:, 1]

            p = pts[i]  # (B,2)
            q = pts[j]
            v = q - p  # (B,2)

            d2 = np.einsum("ij,ij->i", v, v)  # ||q-p||^2, (B,)
            nz = d2 > 0.0
            if not np.all(nz):
                blk = blk[nz]
                i = i[nz]
                j = j[nz]
                p = p[nz]
                q = q[nz]
                v = v[nz]
                d2 = d2[nz]
                if blk.size == 0:
                    continue

            d = np.sqrt(d2)  # (B,)
            r = d / 2.0
            r2 = d2 / 4.0

            # unit normal n = rot90(v)/||v||
            nvec = np.empty_like(v)
            nvec[:, 0] = -v[:, 1]
            nvec[:, 1] = v[:, 0]
            nvec /= d[:, None]

            m_mid = (p + q) / 2.0  # (B,2)

            # finite radii
            R0 = r / (1.0 - abs(g0))
            R1 = r / (1.0 - abs(g1))
            R0_2 = R0 * R0
            R1_2 = R1 * R1

            # offsets along normal
            s0 = np.sqrt(np.maximum(R0_2 - r2, 0.0))
            s1 = np.sqrt(np.maximum(R1_2 - r2, 0.0))

            c0_up = m_mid + s0[:, None] * nvec
            c0_dn = m_mid - s0[:, None] * nvec
            c1_up = m_mid + s1[:, None] * nvec
            c1_dn = m_mid - s1[:, None] * nvec

            B = blk.shape[0]
            empty_any = np.zeros(B, dtype=bool)

            if g0 != 0.0 and g1 != 0.0:
                # two neighborhoods
                if g0 * g1 > 0.0:
                    ca = np.stack([c0_up, c0_dn], axis=1)
                    cb = np.stack([c1_dn, c1_up], axis=1)
                else:
                    ca = np.stack([c0_up, c0_dn], axis=1)
                    cb = np.stack([c1_up, c1_dn], axis=1)

                for k in (0, 1):
                    c_a = ca[:, k, :]
                    c_b = cb[:, k, :]

                    ca_norm2 = np.einsum("ij,ij->i", c_a, c_a)
                    cb_norm2 = np.einsum("ij,ij->i", c_b, c_b)

                    dist_a2 = (
                        pts_norm2[None, :] + ca_norm2[:, None] - 2.0 * (c_a @ pts.T)
                    )
                    dist_b2 = (
                        pts_norm2[None, :] + cb_norm2[:, None] - 2.0 * (c_b @ pts.T)
                    )

                    in_a = comp(dist_a2, R0_2[:, None])
                    in_b = comp(dist_b2, R1_2[:, None])

                    inside = (in_a & in_b) if intersection_mode else (in_a | in_b)

                    inside[np.arange(B), i] = False
                    inside[np.arange(B), j] = False

                    empty_any |= ~inside.any(axis=1)

            else:
                # unique neighborhood
                c_a = c0_up
                c_b = c1_up

                ca_norm2 = np.einsum("ij,ij->i", c_a, c_a)
                cb_norm2 = np.einsum("ij,ij->i", c_b, c_b)

                dist_a2 = pts_norm2[None, :] + ca_norm2[:, None] - 2.0 * (c_a @ pts.T)
                dist_b2 = pts_norm2[None, :] + cb_norm2[:, None] - 2.0 * (c_b @ pts.T)

                in_a = comp(dist_a2, R0_2[:, None])
                in_b = comp(dist_b2, R1_2[:, None])

                inside = (in_a & in_b) if intersection_mode else (in_a | in_b)

                inside[np.arange(B), i] = False
                inside[np.arange(B), j] = False

                empty_any = ~inside.any(axis=1)

            if np.any(empty_any):
                edges_out.extend(map(tuple, blk[empty_any]))

        if edges_out:
            self.graph.add_edges(edges_out)
