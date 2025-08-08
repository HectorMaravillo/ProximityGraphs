import numpy as np
from scipy.spatial import Delaunay
from scipy.spatial import ConvexHull
from scipy.spatial.distance import cdist, pdist
from itertools import combinations
from igraph import Graph

from .points import SetPoints
from .geometricgraphs import GeometricGraph
from .geometricgraphs import load_graph


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
    def __check_parameter(cls, parameter,
                          range_min=None, range_max=None,
                          strict = False,
                          data_type=[int, float, np.float64]):
        if type(parameter) not in data_type:
            raise TypeError()
        inequality = cls.__closed_region(strict)
        if strict:
            strict_text = " or equal "
        else:
            strict_text = " "
        if range_min is not None:
            if inequality(parameter, range_min):
                raise ValueError(f"The parameter is less{strict_text}than "+str(range_min))
        if range_max is not None:
            if inequality(range_max, parameter):
                raise ValueError(f"The parameter is greater{strict_text}than "+str(range_max))

    def __closed_region(cls, strict):
        if strict is True:
            inequality = lambda x, y: x <= y
        else:
            inequality = lambda x, y: x < y
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
            inequality = lambda x, y: x <= y
        else:
            inequality = lambda x, y: x < y
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
        skeleton.details = f"β={beta}, closed={closed}, type={type_region}, (from graph)"
        skeleton._GeometricGraph__setpoints = geom_graph.setpoints
        skeleton._GeometricGraph__graph = Graph()
        skeleton._GeometricGraph__graph.add_vertices(geom_graph.n)
        pairs = np.array(geom_graph.graph.get_edgelist())
        if beta < 1:
            if type_region != "intersection":
                warnings.warn(f"For β<1, the region type {type_region} is undefined.\nUse type_region='intersection'instead.")
            skeleton.__empty_region = lambda p, q: skeleton.__intersection(p, q, beta)
            skeleton.__test = lambda test_1, test_2: test_1*test_2
        elif beta >= 1:
            if type_region not in ["lune", "circle"]:
                raise TypeError("'type_region' must be 'lune' or 'circle' when β > 1.")
            if type_region == "lune":
                skeleton.__empty_region = lambda p, q: skeleton.__lune(p, q, beta)
                skeleton.__test = lambda test_1, test_2: test_1*test_2
            elif type_region == "circle":
                skeleton.__empty_region = lambda p, q: skeleton.__circle(p, q, beta)
                skeleton.__test = lambda test_1, test_2: test_1+test_2
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
                warnings.warn(f"For β<1, the region type {type_region} is undefined.\nUse type_region='intersection'instead.")
            pairs = self.__pairs_by_combinations()
            self.__empty_region = lambda p, q: self.__intersection(p, q, beta)
            self.__test = lambda test_1, test_2: test_1*test_2
        elif beta >= 1:
            if type_region not in ["lune", "circle"]:
                raise TypeError("'type_region' must be 'lune' or 'circle' when β > 1.")
            if beta == 1 and closed is False:
                pairs = self.__pairs_by_combinations()
            else:
                pairs = self.__pairs_by_delaunay()
            if type_region == "lune":
                self.__empty_region = lambda p, q: self.__lune(p, q, beta)
                self.__test = lambda test_1, test_2: test_1*test_2
            elif type_region == "circle":
                self.__empty_region = lambda p, q: self.__circle(p, q, beta)
                self.__test = lambda test_1, test_2: test_1+test_2
        return pairs

    def __assign_edges(self, pairs, beta, closed):
        p = self.points[pairs[:, 0]]
        q = self.points[pairs[:, 1]]
        if beta < 1:
            radius = np.linalg.norm(p-q, axis=1)/(2*beta)
        else:
            radius = np.linalg.norm(p-q, axis=1)*beta/2
        center_1, center_2 = self.__empty_region(p, q)
        edges = []
        for i in np.arange(pairs.shape[0]):
            dist_1 = np.linalg.norm(self.points-center_1[i], axis=1)
            dist_2 = np.linalg.norm(self.points-center_2[i], axis=1)
            if closed:
                empty_test_1 = dist_1 <= radius[i]
                empty_test_2 = dist_2 <= radius[i]
            else:
                empty_test_1 = dist_1 < radius[i]
                empty_test_2 = dist_2 < radius[i]
            empty_test = self.__test(empty_test_1, empty_test_2)
            empty_test = np.delete(empty_test, pairs[i])
            if np.any(empty_test) == False:
                edges.append(pairs[i])
        self.graph.add_edges(edges)

    def __intersection(cls, p, q, beta):
        aux_1 = (p+q)/2
        aux_2 = (q-p) @ cls.matrix_r.T * np.sqrt( 1-np.power(beta, 2) ) / (2*beta)
        center_1 = aux_1 + aux_2
        center_2 = aux_1 - aux_2
        return center_1, center_2
    
    def __circle(cls, p, q, beta):
        aux_1 = (p+q)/2
        aux_2 = (q-p) @ cls.matrix_r.T * np.sqrt(np.power(beta, 2)-1) / 2
        center_1 = aux_1 + aux_2
        center_2 = aux_1 - aux_2
        return center_1, center_2
    
    def __lune(cls, p, q, beta):
        beta_aux = beta/2
        aux = (1-beta_aux)
        center_1 = p*beta_aux + aux*q
        center_2 = q*beta_aux + aux*p
        return center_1, center_2

class RNG(Beta_Skeleton):
    
    # CONSTRUCTOR
    def __init__(self, setpoints, closed=False):
        Beta_Skeleton.__init__(self, setpoints, beta=2, closed=closed)


class GG(Beta_Skeleton):
    
    # CONSTRUCTOR
    def __init__(self, setpoints, closed=True):
        Beta_Skeleton.__init__(self, setpoints, beta=1, closed=closed)




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
    def __init__(self, setpoints, d=2,  k=0, closed=False):
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
        self.details = "d="+str(d)+", k="+str(k)+", closed="+str(closed)
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
        ssg._ProximityGraph__check_parameter(d, range_min=1)
        ssg.name = "Stepping Stone Graph"
        ssg.details = "d="+str(d)+", k="+str(k)+", closed="+str(closed)
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
            dist_pq = np.power(np.linalg.norm(p-q), d)
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
        self.details = "k="+str(k)
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
        self.details = "σ="+str(sigma)+", closed="+str(closed)
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
                if np.any(empty_test_1) == False:
                    # Check empty disk around q
                    dist_2 = np.linalg.norm(self.points - q[i], axis=1)
                    empty_test_2 = self.inequality(dist_2, dist_sigma[i])
                    empty_test_2 = np.delete(empty_test_2, pairs[i])
                    if np.any(empty_test_2) == False:
                        edges.append(pairs[i])
        else: # Iterative approach for larger datasets
            for pair in pairs:
                p = self.points[pair[0]]
                q = self.points[pair[1]]
                dist_sigma = np.linalg.norm(p - q) / sigma
                # Check empty disk around p
                dist_1 = np.linalg.norm(self.points - p, axis=1)
                empty_test_1 = self.inequality(dist_1, dist_sigma)
                empty_test_1 = np.delete(empty_test_1, pair)
                if np.any(empty_test_1) == False:
                    # Check empty disk around q
                    dist_2 = np.linalg.norm(self.points - q, axis=1)
                    empty_test_2 = self.inequality(dist_2, dist_sigma)
                    empty_test_2 = np.delete(empty_test_2, pair)
                    if np.any(empty_test_2) == False:
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
        self.details = "distance max="+str(dist_max)+", closed="+str(closed)
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
        else: # Iterative approach for larger datasets
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
        self.details = "closed="+str(closed)
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
            dist_min_sum = lambda p, q: dist_min[p] + dist_min[q]
            dist_min_sum_vec = np.vectorize(dist_min_sum)
            # Check if distance between pairs is less than sum of radii
            influence = self.inequality(pdist(self.points),
                                        dist_min_sum_vec(pairs[:, 0],
                                                         pairs[:, 1]))
            edges = pairs[influence]
        else: # Iterative approach for larger datasets
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

    def __init__(self, setpoints, alpha=1.5):
        """
        Initializes an Elliptic_GabrielG object.

        Parameters
        ----------
        setpoints : SetPoints
            An object containing the set of points.
        alpha : float, optional
            The elongation factor of the ellipse. Must be >= 1.
        """
        self._ProximityGraph__check_parameter(alpha, range_min=1)
        ProximityGraph.__init__(self, setpoints)
        self.name = "Elliptic Gabriel Graph"
        self.details = "α=" + str(alpha)
        self.__assign_edges(alpha)
        self.graph.simplify()
        self._GeometricGraph__size()
        self._GeometricGraph__add_lengths()

    def __assign_edges(self, alpha):
        """
        Assigns edges based on the elliptical empty region condition.

        Parameters
        ----------
        alpha : float
            The elliptic elongation factor.
        """
        pts = self.points
        n = self.n
        edges = []

        # Use GG to reduce candidate edges
        g_gabriel = GG(self.setpoints)
        pairs = np.array(g_gabriel.graph.get_edgelist())

        for i, j in pairs:
            p, q = pts[i], pts[j]
            dist_pq = np.linalg.norm(p - q)
            threshold = alpha * dist_pq
            # Compute sum of distances to all other points
            dist_to_foci = np.linalg.norm(pts - p, axis=1) + np.linalg.norm(pts - q, axis=1)
            mask = np.ones(n, dtype=bool)
            mask[[i, j]] = False
            if np.all(dist_to_foci[mask] > threshold):
                edges.append((i, j))

        self.graph.add_edges(edges)

    @classmethod
    def from_graph(cls, geom_graph, alpha=1.5):
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
        egg._ProximityGraph__check_parameter(alpha, range_min=1)
        egg.name = "Elliptic Gabriel Graph"
        egg.details = "α=" + str(alpha)
        egg._GeometricGraph__setpoints = geom_graph.setpoints
        egg._GeometricGraph__graph = Graph()
        egg._GeometricGraph__graph.add_vertices(geom_graph.n)
        egg.points = geom_graph.points
        egg.n = geom_graph.n

        pts = egg.points
        n = egg.n
        edges = []

        g_gabriel = GG.from_graph(geom_graph, beta=1, closed=True)
        pairs = np.array(g_gabriel.graph.get_edgelist())

        for i, j in pairs:
            p, q = pts[i], pts[j]
            dist_pq = np.linalg.norm(p - q)
            threshold = alpha * dist_pq
            dist_to_foci = np.linalg.norm(pts - p, axis=1) + np.linalg.norm(pts - q, axis=1)
            mask = np.ones(n, dtype=bool)
            mask[[i, j]] = False
            if np.all(dist_to_foci[mask] > threshold):
                edges.append((i, j))

        egg.graph.add_edges(edges)
        egg.graph.simplify()
        egg._GeometricGraph__size()
        egg._GeometricGraph__add_lengths()
        return egg