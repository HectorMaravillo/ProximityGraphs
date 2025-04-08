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

    # CONSTRUCTOR
    def __init__(self, setpoints):
        GeometricGraph.__init__(self, setpoints)
        self.name = "Proximity Graph"

    @classmethod
    def from_graph(cls, geom_graph):
        setpoints = geom_graph.setpoints
        proximity_graph = cls(setpoints)
        proximity_graph._GeometricGraph__add_lengths()
        return proximity_graph

    # METHODS
    def __check_parameter(cls, parameter,
                          range_min=None, range_max=None,
                          data_type=[int, float, np.float64]):
        if type(parameter) not in data_type:
            raise TypeError()
        if range_min is not None:
            if parameter < range_min:
                raise ValueError("The parameter is less than "+str(range_min))
        if range_max is not None:
            if parameter > range_max:
                raise ValueError("The parameter is greater than "+str(range_max))

    def __closed_region(cls, closed):
        if closed is True:
            inequality = lambda x, y: x <= y
        else:
            inequality = lambda x, y: x < y
        return inequality


class DelaunayG(ProximityGraph):

    # CONSTRUCTOR
    def __init__(self, setpoints):
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

    # CONSTRUCTOR
    def __init__(self, setpoints):
        ProximityGraph.__init__(self, setpoints)
        self.name = "Convex Hull"
        hull = ConvexHull(setpoints.points)
        self.graph.add_edges(hull.simplices)
        self.graph.simplify()
        self._GeometricGraph__size()
        self._GeometricGraph__add_lengths()

    # Methods
    def vertices(self):
        convex_hull_v = self.graph.vs.select(_degree=2).indices
        return SetPoints(self.points[convex_hull_v])


class MST(ProximityGraph):

    # CONSTRUCTOR
    def __init__(self, setpoints):
        ProximityGraph.__init__(self, setpoints)
        self.name = "Minimum Spanning Tree"
        d = DelaunayG(setpoints)
        mst = d.graph.spanning_tree(weights=d.graph.es["dist_eucl"])
        self._GeometricGraph__graph = mst
        self.graph.simplify()
        self._GeometricGraph__size()


class Beta_Skeleton(ProximityGraph):

    # CONSTRUCTOR
    def __init__(self, setpoints, beta=1.5, type_region="lune", closed=False):
        self._ProximityGraph__check_parameter(beta, range_min=0)
        ProximityGraph.__init__(self, setpoints)
        self.name = "β-Skeleton"
        self.details = "β="+str(beta)
        if beta >= 1:
            g_delaunay = DelaunayG(setpoints)
            pairs = np.array(g_delaunay.graph.get_edgelist())
            if type_region == "lune":
                empty_region = lambda p, q: self.__lune(p, q, beta)
                self.__test = lambda test_1, test_2: test_1*test_2
        self.__empty_region = np.vectorize(empty_region)
        self.__assign_edges(pairs, beta)
        self.graph.simplify()
        self._GeometricGraph__size()
        self._GeometricGraph__add_lengths()

    @classmethod
    def from_graph(cls, geom_graph, beta=1.5, closed=False):
        skeleton = cls.__new__(cls)
        skeleton._ProximityGraph__check_parameter(beta, range_min=1)
        skeleton.name = "β-Skeleton"
        skeleton.details = "β="+str(beta)
        skeleton._GeometricGraph__setpoints = geom_graph.setpoints
        skeleton._GeometricGraph__graph = Graph()
        skeleton._GeometricGraph__graph.add_vertices(geom_graph.n)
        pairs = np.array(geom_graph.graph.get_edgelist())
        empty_region = lambda p, q: skeleton.__lune(p, q, beta)
        skeleton.__test = lambda test_1, test_2: test_1*test_2
        skeleton.__empty_region = np.vectorize(empty_region)
        skeleton.__assign_edges(pairs, beta)
        skeleton.graph.simplify()
        skeleton._GeometricGraph__size()
        skeleton._GeometricGraph__add_lengths()
        return skeleton

    # Methods
    def __assign_edges(self, pairs, beta):
        p = self.points[pairs[:, 0]]
        q = self.points[pairs[:, 1]]
        if beta >= 1:
            radius = np.linalg.norm(p-q, axis=1)*beta/2
        center_1, center_2 = self.__empty_region(p, q)
        edges = []
        for i in np.arange(pairs.shape[0]):
            dist_1 = np.linalg.norm(self.points-center_1[i], axis=1)
            dist_2 = np.linalg.norm(self.points-center_2[i], axis=1)
            empty_test_1 = dist_1 <= radius[i]
            empty_test_2 = dist_2 <= radius[i]
            empty_test = self.__test(empty_test_1, empty_test_2)
            empty_test = np.delete(empty_test, pairs[i])
            if np.any(empty_test) == False:
                edges.append(pairs[i])
        self.graph.add_edges(edges)

    def __lune(cls, p, q, beta):
        beta_aux = beta/2
        center_1 = p*beta_aux + (1-beta_aux)*q
        center_2 = q*beta_aux + (1-beta_aux)*p
        return center_1, center_2


class Stepping_Stone(ProximityGraph):

    # CONSTRUCTOR
    def __init__(self, setpoints, d=2,  k=0, closed=False):
        self._ProximityGraph__check_parameter(d, range_min=1)
        self._ProximityGraph__check_parameter(k, range_min=0, data_type=[int])
        ProximityGraph.__init__(self, setpoints)
        self.name = "Stepping Stone Graph"
        self.details = "d="+str(d)+", k="+str(k)+", closed="+str(closed)
        self.__inequality = self._ProximityGraph__closed_region(closed)
        if d >= 1 and d < 2:
            pairs = combinations(range(self.n), 2)
        elif d >= 2:
            g_delaunay = DelaunayG(self.setpoints)
            pairs = np.array(g_delaunay.graph.get_edgelist())
        self.__assign_edges(pairs, d, k)
        self.graph.simplify()
        self._GeometricGraph__size()
        self._GeometricGraph__add_lengths()

    @classmethod
    def from_graph(cls, geom_graph, d=2, closed=False):
        ssg = cls.__new__(cls)
        ssg.ssg(d, range_min=2)
        ssg.name = "Stepping Stone Graph"
        ssg.details = "d="+str(d)+", k=0, closed="+str(closed)
        ssg._GeometricGraph__setpoints = geom_graph.setpoints
        ssg._GeometricGraph__graph = Graph()
        ssg._GeometricGraph__graph.add_vertices(geom_graph.n)
        pairs = np.array(geom_graph.graph.get_edgelist())
        ssg.__assign_edges(pairs, d, k=0)
        ssg.graph.simplify()
        ssg._GeometricGraph__size()
        ssg._GeometricGraph__add_lengths()
        return ssg

    # Methods
    def __assign_edges(self, pairs, d, k):
        edges = []
        for pair in pairs:
            p = self.points[pair[0]]
            q = self.points[pair[1]]
            dist_pq = np.power(np.linalg.norm(p-q), d)
            dist_1 = np.power(np.linalg.norm(self.points-p, axis=1), d)
            dist_2 = np.power(np.linalg.norm(self.points-q, axis=1), d)
            empty_test = self.__inequality(dist_1 + dist_2, dist_pq)
            empty_test = np.delete(empty_test, pair)
            if empty_test.sum() <= k:
                edges.append((pair[0], pair[1]))
        self._GeometricGraph__graph.add_edges(edges)


class NNG(ProximityGraph):

    # CONSTRUCTOR
    def __init__(self, setpoints, k=1):
        self._ProximityGraph__check_parameter(k, range_min=1, data_type=[int])
        ProximityGraph.__init__(self, setpoints)
        self.name = "Nearest Neighbor Graph"
        self.details = "k="+str(k)
        self.__assign_edges(k)
        self.graph.simplify()
        self._GeometricGraph__size()
        self._GeometricGraph__add_lengths()

    def __assign_edges(self, k):
        edges = []
        if self.n <= self._GeometricGraph__limit_vec:
            dist_matrix = cdist(self.points, self.points)
            dist_matrix = dist_matrix + np.diag(np.inf*np.ones(self.n))
            for _k in range(k):
                arg_min = np.argmin(dist_matrix, axis=1)
                nearest_neighbors = list(enumerate(arg_min))
                edges = edges + nearest_neighbors
                nn_array = np.array(nearest_neighbors)
                dist_matrix[nn_array[:, 0], nn_array[:, 1]] = np.inf
        else:
            for i in range(self.n):
                dist = np.linalg.norm(self.points-self.points[i], axis=1)
                dist[i] = np.inf
                for _k in range(k):
                    arg_min = np.argmin(dist)
                    edges.append((i, arg_min))
                    dist[arg_min] = np.inf
        self._GeometricGraph__graph.add_edges(edges)


class Sigma_Graph(ProximityGraph):

    # CONSTRUCTOR
    def __init__(self, setpoints, sigma=1, closed=False):
        self._ProximityGraph__check_parameter(sigma, range_min=1)
        ProximityGraph.__init__(self, setpoints)
        self.name = "σ-Graph"
        self.details = "σ="+str(sigma)+", closed="+str(closed)
        self.inequality = self._ProximityGraph__closed_region(closed)
        self.__assign_edges(sigma)
        self.graph.simplify()
        self._GeometricGraph__size()
        self._GeometricGraph__add_lengths()

    def __assign_edges(self, sigma):
        pairs = combinations(range(self.n), 2)
        edges = []
        if self.n <= self._GeometricGraph__limit_vec:
            pairs = np.array(list(pairs))
            p = self.points[pairs[:, 0]]
            q = self.points[pairs[:, 1]]
            dist_sigma = pdist(self.points)/sigma
            for i in np.arange(pairs.shape[0]):
                dist_1 = np.linalg.norm(self.points-p[i], axis=1)
                empty_test_1 = self.inequality(dist_1, dist_sigma[i])
                empty_test_1 = np.delete(empty_test_1, pairs[i])
                if np.any(empty_test_1) == False:
                    dist_2 = np.linalg.norm(self.points-q[i], axis=1)
                    empty_test_2 = self.inequality(dist_2, dist_sigma[i])
                    empty_test_2 = np.delete(empty_test_2, pairs[i])
                    if np.any(empty_test_2) == False:
                        edges.append(pairs[i])
        else:
            for pair in pairs:
                p = self.points[pair[0]]
                q = self.points[pair[1]]
                dist_sigma = np.linalg.norm(p-q)/sigma
                dist_1 = np.linalg.norm(self.points-p, axis=1)
                empty_test_1 = self.inequality(dist_1, dist_sigma)
                empty_test_1 = np.delete(empty_test_1, pair)
                if np.any(empty_test_1) == False:
                    dist_2 = np.linalg.norm(self.points-q, axis=1)
                    empty_test_2 = self.inequality(dist_2, dist_sigma)
                    empty_test_2 = np.delete(empty_test_2, pair)
                    if np.any(empty_test_2) == False:
                        edges.append((pair[0], pair[1]))
        self._GeometricGraph__graph.add_edges(edges)


class Unit_Disk(ProximityGraph):

    # CONSTRUCTOR
    def __init__(self, setpoints, dist_max, closed=True):
        self._ProximityGraph__check_parameter(dist_max, range_min=0)
        ProximityGraph.__init__(self, setpoints)
        self.name = "Unit Disk Graph"
        self.details = "distance max="+str(dist_max)+", closed="+str(closed)
        self.inequality = self._ProximityGraph__closed_region(closed)
        self.__assign_edges(dist_max)
        self.graph.simplify()
        self._GeometricGraph__size()
        self._GeometricGraph__add_lengths()

    def __assign_edges(self, dist_max):
        if self.n <= self._GeometricGraph__limit_vec:
            pairs = combinations(range(self.n), 2)
            pairs = np.array(list(pairs))
            dist_pairs = pdist(self.points)
            dist_disk = self.inequality(dist_pairs, dist_max)
            edges = pairs[dist_disk == True]
        else:
            edges = []
            for i in range(self.n):
                dist = np.linalg.norm(self.points-self.points[i], axis=1)
                dist[i] = np.inf
                dist_enum = enumerate(dist)
                edges_aux = [(i, j) for j, v in dist_enum if self.inequality(v, dist_max)]
                edges = edges + edges_aux
        self._GeometricGraph__graph.add_edges(edges)


class SIG(ProximityGraph):

    # CONSTRUCTOR
    def __init__(self, setpoints, closed=False):
        ProximityGraph.__init__(self, setpoints)
        self.name = "Sphere Influence Graph"
        self.details = "closed="+str(closed)
        self.inequality = self._ProximityGraph__closed_region(closed)
        self.__assign_edges()
        self.graph.simplify()
        self._GeometricGraph__size()
        self._GeometricGraph__add_lengths()

    def __assign_edges(self):
        pairs = combinations(range(self.n), 2)
        dist_min = self._GeometricGraph__dist_nearest()
        if self.n <= self._GeometricGraph__limit_vec:
            pairs = np.array(list(pairs))
            dist_min_sum = lambda p, q: dist_min[p]+dist_min[q]
            dist_min_sum_vec = np.vectorize(dist_min_sum)
            influence = self.inequality(pdist(self.points),
                                        dist_min_sum_vec(pairs[:, 0],
                                                         pairs[:, 1]))
            edges = pairs[influence == True]
        else:
            edges = []
            for p, q in pairs:
                dist = np.linalg.norm(self.points[p]-self.points[q])
                if self.inequality(dist, dist_min[p]+dist_min[q]):
                    edges.append((p, q))
        self.graph.add_edges(edges)
