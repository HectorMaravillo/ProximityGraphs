import igraph as ig
import numpy as np

from scipy.spatial.distance import cdist
from matplotlib.pyplot import subplots
from geopandas import GeoDataFrame
from geopandas import GeoSeries
from shapely.geometry import LineString
from shapely.ops import polygonize
from scipy.stats import entropy

from .points import SetPoints


class GeometricGraph:

    # ATTRIBUTES
    @property
    def points(self):
        return self.__setpoints.points

    @property
    def setpoints(self):
        return self.__setpoints

    @property
    def n(self):
        return self.__setpoints.n

    @property
    def m(self):
        return self.__m

    @property
    def cc(self):
        return len(self.graph.connected_components())

    @property
    def f(self):
        return self.cc-self.n+self.m+1

    @property
    def graph(self):
        return self.__graph

    @property
    def name(self):
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
        degrees = self.graph.degree()
        degrees_sequence = [degrees.count(i) for i in range(1, max(degrees)+1)]
        return np.array(degrees_sequence)

    @property
    def lengths(self):
        if self.m == 0:
            return np.array([])
        else:
            return np.array(self.graph.es["dist_eucl"])

    @property
    def orientation(self):
        if "orientation" in self.graph.es.attribute_names():
            return np.array(self.graph.es["orientation"])
        else:
            return self.__add_orientation()

    __limit_vec = 20000

    # CONSTRUCTOR
    def __init__(self, setpoints):
        self.__setpoints = setpoints
        self.__graph = ig.Graph()
        self.__graph.add_vertices(self.n)
        self.__m = 0
        self.__name = "Geometric Graph"
        self.__details = ""

    @classmethod
    def complete(cls, setpoints):
        complete_graph = cls.__new__(cls)
        complete_graph.__setpoints = setpoints
        complete_graph.__graph = ig.Graph.Full(n=setpoints.n)
        complete_graph._GeometricGraph__size()
        complete_graph._GeometricGraph__add_lengths()
        complete_graph.__name = "Complete Graph"
        complete_graph.__details = ""
        return complete_graph

    @classmethod
    def from_graph(cls, graph, points, name=None):
        setpoints = SetPoints(points)
        geometricgraph = cls.__new__(cls)
        geometricgraph.__setpoints = setpoints
        geometricgraph.__graph = graph
        if name is None:
            geometricgraph.__name = "Original Graph"
        else:
            geometricgraph.__name = name
        geometricgraph.__details = ""
        geometricgraph.__size()
        geometricgraph.__add_lengths()
        return geometricgraph

    # METHODS
    
    def copy(self):
        new_graph = GeometricGraph(self.setpoints)
        new_graph._GeometricGraph__graph = self.graph.copy()
        new_graph._GeometricGraph__size()
        new_graph.name = self.__name
        new_graph.details = self.__details
        return new_graph

    def __size(self):
        self.__m = self.__graph.ecount()
        return self.__m

    def __add_lengths(self):
        edges = np.array(self.graph.get_edgelist())
        edges_pos_x = self.points[edges[:, 0]]
        edges_pos_y = self.points[edges[:, 1]]
        length = np.linalg.norm(edges_pos_x-edges_pos_y, axis=1)
        self.graph.es["dist_eucl"] = length

    def __add_orientation(self):
        if self.m > 0:
            edges = self.graph.get_edgelist()
            pos = self.setpoints.pos
            coords = [(pos[u][0], pos[u][1], pos[v][0], pos[v][1])
                      for u, v in edges]
            coords = np.array(coords)
            dist_x = coords[:, 0] - coords[:, 2]
            dist_y = coords[:, 1] - coords[:, 3]
            angle = np.arctan(dist_y/dist_x)
            orientation = np.degrees(np.pi/2 - angle)
            self.graph.es["orientation"] = orientation
        else:
            orientation = np.array([])
        return np.array(orientation)

    def entropy(self, variable_name, bins=10):
        if variable_name == "orientation":
            bin_counts, _ = np.histogram(self.orientation, bins)
        if variable_name == "length":
            bin_counts, _ = np.histogram(self.lengths, bins)
        elif variable_name == "degree":
            bin_counts, _ = np.histogram(self.degree, bins)
        return entropy(bin_counts)

    def __draw_graph(self, graph, points, ax,
                     v_size, v_color, e_size, e_color):
        ax = ig.plot(graph, target=ax,
                     vertex_size=v_size,
                     vertex_color=v_color,
                     edge_width=e_size,
                     edge_color=e_color,
                     layout=points,
                     autocurve=False,
                     keep_aspect_ratio=True)
        return ax

    def draw(self, figsize=(15, 15),
             v_size=5, v_color="black",
             e_size=1, e_color="black",
             title=True, fontsize=12, details=False):
        fig, ax = subplots(figsize=figsize)
        ax = self.__draw_graph(graph=self.__graph, points=self.points, ax=ax,
                               v_size=v_size,  v_color=v_color,
                               e_size=e_size, e_color=e_color)
        return fig, ax

    def draw_orientation(self, num_bins=36, figsize=(5, 5),
                         color="darkgreen",  area=False):
        orientation = self.orientation
        orientation_double = (orientation+180) % 360
        orientation = np.concatenate((orientation, orientation_double),
                                     axis=0)
        bin_counts, bin_edges = np.histogram(orientation,
                                             range=(0, 360), bins=num_bins)
        width = 2*np.pi/num_bins
        bin_frequency = bin_counts/bin_counts.sum()
        if area:
            radius = np.sqrt(bin_frequency)
        else:
            radius = bin_frequency
        positions = np.radians(bin_edges[:-1])
        fig, ax = subplots(figsize=figsize, subplot_kw={"projection": "polar"})
        ax.set_theta_zero_location("N")
        ax.set_theta_direction("clockwise")
        ax.set_ylim(top=radius.max())
        ax.set_yticks(np.linspace(0, radius.max(), 5))
        ax.set_yticklabels(labels="")
        xticklabels = ["N", "", "E", "", "S", "", "O", ""]
        ax.set_xticks(ax.get_xticks())
        ax.set_xticklabels(labels=xticklabels)
        ax.tick_params(axis="x", which="major", pad=-2)
        ax.bar(
                positions,
                height=radius,
                width=width,
                align="center",
                bottom=0,
                zorder=2,
                color=color,
                edgecolor="black",
                linewidth=0.5,
                alpha=0.7,
            )
        return fig, ax

    def __dist_nearest(self):
        i = range(0, self.n)
        if self.n <= self.__limit_vec:
            dist = cdist(self.points, self.points)
            dist[i, i] = np.inf
            dist_min = np.min(dist, axis=1)
        else:
            dist_min = []
            for i in range(self.n):
                dist = np.linalg.norm(self.points-self.points[i], axis=1)
                dist[i] = np.inf
                dist_min.append(np.min(dist))
        return dist_min

    def union(self, other):
        g = ig.union([self.graph, other.graph], byname=False)
        union_g = GeometricGraph.from_graph(g, self.points)
        union_g.__details = "Union"
        return union_g

    def intersection(self, other):
        g = ig.intersection([self.graph, other.graph], byname=False)
        intersection_g = GeometricGraph.from_graph(g, self.points)
        intersection_g.__details = "Intersection"
        return intersection_g

    def difference(self, other):
        edges_g = set(self.graph.get_edgelist())
        edges_h = set(other.graph.get_edgelist())
        edges = edges_g.difference(edges_h)
        difference_g = GeometricGraph(self.setpoints)
        if len(edges) > 0:
            difference_g.__graph.add_edges(edges)
            difference_g.__size()
            difference_g.__add_lengths()
        difference_g.__details = "Difference"
        return difference_g

    def symmetric_difference(self, other):
        edges_g_h = set(self.graph.get_edgelist())
        edges_h_g = set(other.graph.get_edgelist())
        edges = edges_g_h.symmetric_difference(edges_h_g)
        symmetric_g = GeometricGraph(self.setpoints)
        if len(edges) > 0:
            symmetric_g.__graph.add_edges(edges)
            symmetric_g.__size()
            symmetric_g.__add_lengths()
        symmetric_g.__details = "Symmetric Difference"
        return symmetric_g

    def recovering(self, other, distance="R"):
        union = self.union(other)
        if distance == "R":
            symmetric = self.symmetric_difference(other)
            return symmetric.m/union.m

    def save(self, path, filename):
        self.__graph["name"] = self.name
        self.__graph["details"] = self.details
        self.__graph.write_pickle(path+filename)
        np.save(path+filename, self.points)
        del self.__graph["name"], self.__graph["details"]

    def to_gpd_lines(self):
        lines = lambda edge:  LineString([self.setpoints.pos[edge[0]],
                                          self.setpoints.pos[edge[1]]])
        edges = self.graph.get_edgelist()
        geometry = map(lines, edges)
        gpd_lines = GeoDataFrame(geometry=GeoSeries(geometry))
        attr_names = self.graph.es.attribute_names()
        for variable in attr_names:
            attribute = self.graph.es[variable]
            gpd_lines[variable] = attribute
        gpd_lines["union_initial"] = np.array(edges)[:, 0]
        gpd_lines["union_final"] = np.array(edges)[:, 1]
        columns = ["union_initial", "union_final"]+attr_names+["geometry"]
        return gpd_lines[columns]

    def to_gpd_polygons(self):
        if self.cc-self.n+self.m > 0:
            gpd_graph = self.to_gpd_lines()
            geom = polygonize(gpd_graph["geometry"])
            geom = list(geom)
            return GeoDataFrame(geometry=list(geom))
        else:
            raise TypeError("The graph has only one face")


def load_graph(path, filename):
    points = np.load(path+filename+".npy")
    graph = ig.Graph.Read_Pickle(path+filename)
    load_graph = GeometricGraph.from_graph(graph, points)
    load_graph.name = graph["name"]
    load_graph.details = graph["details"]
    del load_graph._GeometricGraph__graph["name"]
    del load_graph._GeometricGraph__graph["details"]
    return load_graph
