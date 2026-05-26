import warnings

import igraph as ig
import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.pyplot import subplots
from scipy.spatial.distance import cdist
from scipy.stats import entropy

from .points import SetPoints


def _require_gis_dependencies():
    try:
        from geopandas import GeoDataFrame, GeoSeries
    except ImportError as exc:
        raise ImportError(
            "GeoDataFrame export requires the optional GIS dependencies. "
            "Install them with: pip install -e .[gis]"
        ) from exc

    try:
        from shapely.geometry import LineString
        from shapely.ops import polygonize
    except ImportError as exc:
        raise ImportError(
            "Polygon and line export requires the optional GIS dependencies. "
            "Install them with: pip install -e .[gis]"
        ) from exc

    return GeoDataFrame, GeoSeries, LineString, polygonize


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

    @classmethod
    def complete(cls, setpoints):
        if not isinstance(setpoints, SetPoints):
            raise TypeError("Input 'setpoints' must be an instance of SetPoints.")
        complete_graph_instance = cls.__new__(cls)
        complete_graph_instance.__setpoints = setpoints
        complete_graph_instance.__graph = ig.Graph.Full(n=setpoints.n)
        complete_graph_instance._GeometricGraph__m = (
            complete_graph_instance.__graph.ecount()
        )
        complete_graph_instance._GeometricGraph__add_lengths()
        complete_graph_instance.__name = "Complete Graph"
        complete_graph_instance.__details = f"K_{setpoints.n}"
        return complete_graph_instance

    @classmethod
    def from_graph(cls, graph, points, name=None):
        setpoints_instance = SetPoints(points)
        if graph.vcount() != setpoints_instance.n:
            raise ValueError("Number of vertices in graph must match number of points.")
        geometric_graph_instance = cls.__new__(cls)
        geometric_graph_instance.__setpoints = setpoints_instance
        geometric_graph_instance.__graph = graph.copy()
        if name is None:
            geometric_graph_instance.__name = "Imported Graph"
        else:
            geometric_graph_instance.__name = name
        geometric_graph_instance.__details = "Constructed from existing igraph.Graph"
        geometric_graph_instance._GeometricGraph__m = (
            geometric_graph_instance.__graph.ecount()
        )
        geometric_graph_instance.__add_lengths()
        return geometric_graph_instance

    @classmethod
    def random_graph(cls, setpoints, p: float, seed: int | None = None):
        if not isinstance(setpoints, SetPoints):
            raise TypeError("Input 'setpoints' must be an instance of SetPoints.")
        if not (0.0 <= p <= 1.0):
            raise ValueError("Connection probability 'p' must be in the range [0, 1].")
        instance = cls.__new__(cls)
        instance.__setpoints = setpoints
        instance.__graph = ig.Graph.Erdos_Renyi(
            n=setpoints.n, p=p, directed=False, loops=False
        )
        instance._GeometricGraph__m = instance.__graph.ecount()
        instance._GeometricGraph__add_lengths()
        instance.__name = "Random Graph"
        details_str = f"G({setpoints.n}, p={p:.3g}"
        if seed is not None:
            details_str += f", seed={seed}"
        details_str += ")"
        instance.__details = details_str
        return instance

    def copy(self):
        new_setpoints = self.setpoints.copy()
        new_graph_instance = self.__class__.__new__(self.__class__)
        new_graph_instance._GeometricGraph__setpoints = new_setpoints
        new_graph_instance._GeometricGraph__graph = self.graph.copy()
        new_graph_instance._GeometricGraph__m = self.m
        new_graph_instance._GeometricGraph__name = self.name
        new_graph_instance._GeometricGraph__details = self.details
        return new_graph_instance

    def __size(self):
        self.__m = self.__graph.ecount()
        return self.__m

    def __add_lengths(self):
        if self.m > 0:
            edges = np.array(self.graph.get_edgelist())
            points_for_calc = self.points
            if points_for_calc.ndim == 1:
                pass
            edges_pos_x = points_for_calc[edges[:, 0]]
            edges_pos_y = points_for_calc[edges[:, 1]]
            length = np.linalg.norm(edges_pos_x - edges_pos_y, axis=1)
            self.graph.es["dist_eucl"] = length
        else:
            self.graph.es["dist_eucl"] = []

    def __add_orientation(self):
        if self.m == 0:
            return np.array([])
        calculated_orientations = np.array([])
        try:
            edges = self.graph.get_edgelist()
            if not edges:
                return np.array([])
            points_arr = self.points
            if (
                not isinstance(points_arr, np.ndarray)
                or points_arr.ndim < 2
                or points_arr.shape[0] < 2
                or points_arr.shape[1] < 2
            ):
                warnings.warn(
                    "Orientation calculation requires a NumPy array of at least 2"
                    "points in at least 2 dimensions.",
                    stacklevel=2,
                )
                return np.array([])
            dim = points_arr.shape[1]
            coords_u = points_arr[np.array(edges)[:, 0]]
            coords_v = points_arr[np.array(edges)[:, 1]]
            if dim == 2:
                dx = coords_v[:, 0] - coords_u[:, 0]
                dy = coords_v[:, 1] - coords_u[:, 1]
                ang = np.degrees(np.arctan2(dy, dx))
                calculated_orientations = np.mod(ang, 360)
            elif dim == 3:
                dx = coords_v[:, 0] - coords_u[:, 0]
                dy = coords_v[:, 1] - coords_u[:, 1]
                dz = coords_v[:, 2] - coords_u[:, 2]
                azimuth = np.mod(np.degrees(np.arctan2(dy, dx)), 360)
                horiz_len = np.hypot(dx, dy)
                elevation = np.full_like(dz, 0.0, dtype=float)
                non_vertical_mask = horiz_len != 0
                elevation[non_vertical_mask] = np.degrees(
                    np.arctan2(dz[non_vertical_mask], horiz_len[non_vertical_mask])
                )
                vertical_mask = horiz_len == 0
                elevation[vertical_mask] = np.copysign(90.0, dz[vertical_mask])
                calculated_orientations = np.column_stack((azimuth, elevation))
            else:
                msg = (
                    "Orientation is defined only for 2-D or 3-D layouts "
                    f"(received {dim}-D). No values were written."
                )
                warnings.warn(
                    msg,
                    stacklevel=2,
                )
            if calculated_orientations.size > 0 and hasattr(self.graph, "es"):
                self.graph.es["orientation"] = calculated_orientations.tolist()
            return calculated_orientations
        except Exception as exc:
            warnings.warn(
                f"Could not compute edge orientations due to exception: {exc}",
                stacklevel=2,
            )
            return np.array([])

    def entropy(self, variable_name, bins=10):
        if variable_name == "orientation":
            data = self.orientation
        elif variable_name == "length":
            data = self.lengths
        elif variable_name == "degree":
            if self.n == 0:
                return 0.0
            data = self.graph.degree()
        else:
            raise ValueError(
                "Unsupported variable_name for entropy: "
                f"{variable_name}. Choose from 'orientation', 'length', "
                "'degree'."
            )
        if len(data) == 0:
            return 0.0
        bin_counts, _ = np.histogram(data, bins=bins)
        bin_counts = bin_counts[bin_counts > 0]
        if len(bin_counts) == 0:
            return 0.0
        return entropy(bin_counts, base=2)

    def draw_orientation(
        self,
        num_bins: int = 36,
        figsize: tuple[int, int] = (5, 5),
        color: str = "darkgreen",
        area: bool = False,
        component: str = "auto",
    ):
        orientation = self.orientation
        if orientation.ndim == 1:
            angles = orientation
        elif orientation.ndim == 2 and orientation.shape[1] == 2:
            if component == "auto":
                component = "azimuth"
            comp_idx = {"azimuth": 0, "elevation": 1}.get(component)
            if comp_idx is None:
                raise ValueError(
                    "component must be 'azimuth', 'elevation' or 'auto' "
                    f"(received {component!r})"
                )
            angles = orientation[:, comp_idx]
            if component == "elevation":
                angles = (angles + 90) % 180
        else:
            msg = (
                f"Orientation array has unexpected shape {orientation.shape}; "
                "cannot plot."
            )
            warnings.warn(
                msg,
                stacklevel=2,
            )
            return None, None

        if angles.size == 0:
            warnings.warn(
                "No orientation data to plot for draw_orientation.", stacklevel=2
            )
            fig, ax = subplots(figsize=figsize, subplot_kw={"projection": "polar"})
            ax.set_title("Edge orientation distribution (No data)")
            return fig, ax

        angles_doubled = (angles + 180) % 360
        angles_all = np.concatenate((angles, angles_doubled), axis=0)

        bin_counts, bin_edges = np.histogram(angles_all, range=(0, 360), bins=num_bins)
        if bin_counts.sum() == 0:
            warnings.warn("All bin counts are zero in draw_orientation.", stacklevel=2)
            fig, ax = subplots(figsize=figsize, subplot_kw={"projection": "polar"})
            ax.set_title("Edge orientation distribution (All bins empty)")
            return fig, ax

        bin_freq = bin_counts / bin_counts.sum()
        radius = np.sqrt(bin_freq) if area else bin_freq
        width = 2 * np.pi / num_bins
        positions = np.radians(bin_edges[:-1])
        fig, ax = subplots(figsize=figsize, subplot_kw={"projection": "polar"})
        ax.set_theta_zero_location("N")
        ax.set_theta_direction("clockwise")
        ax.set_ylim(top=radius.max() if radius.size > 0 else 1.0)
        ax.set_yticks(np.linspace(0, ax.get_ylim()[1], 5))
        ax.set_yticklabels(labels="")
        ax.set_xticks(ax.get_xticks())
        ax.set_xticklabels(["N", "", "E", "", "S", "", "W", ""])
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
        ax.set_title(
            f"Edge {component} distribution"
            if orientation.ndim == 2
            else "Edge orientation distribution"
        )
        return fig, ax

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
        transparent=True,
        *,
        ax=None,
        fig_kwargs=None,
        v_kwargs=None,
        e_kwargs=None,
        title_kwargs=None,
        savefig_kwargs=None,
    ):
        """
        Draws the geometric graph using Matplotlib.

        Parameters
        ----------
        figsize : tuple of (float, float), optional
            Figure size in inches. Default ``(15, 15)``.
        v_size : float, optional
            Marker size for vertices. ``0`` disables vertex scatter. Default 5.
        v_color : str, optional
            Vertex color passed to Matplotlib. Default ``"black"``.
        v_alpha : float, optional
            Vertex alpha level between 0 (transparent) and 1 (opaque).
            Default 1.
        e_size : float, optional
            Line width for boundary edges. Default 1.
        e_color : str, optional
            Color for boundary edges. Default ``"black"``.
        e_alpha : float, optional
            Edge alpha level between 0 (transparent) and 1 (opaque).
            Default 1.
        title : bool, optional
            Whether to set a title. Default True.
        fontsize : float, optional
            Title font size. Default 12.
        details : bool, optional
            If True, appends ``details`` to the title. Default False.
        axis : bool, optional
            If True, show axes. Default False.
        save : str or None, optional
            If set, saves a ``.png`` at ``save + ".png"``.
            If ``None``, returns the live figure and axes. Default ``None``.
        transparent : bool, optional
            If True and ``save`` is set, saves the PNG with a transparent
            background. Default False.

        Other Parameters
        ----------------
        fig_kwargs : dict, optional
            Extra keyword arguments passed to ``matplotlib.pyplot.subplots``.
        v_kwargs : dict, optional
            Extra keyword arguments passed to ``ax.scatter`` (vertex scatter).
            These override ``v_size``, ``v_color``, ``v_alpha`` if duplicated.
        e_kwargs : dict, optional
            Extra keyword arguments passed to ``matplotlib.collections.LineCollection``.
            These override ``e_size``, ``e_color``, ``e_alpha`` if duplicated.
        title_kwargs : dict, optional
            Extra keyword arguments passed to ``ax.set_title``.
            These override ``fontsize`` if duplicated.
        savefig_kwargs : dict, optional
            Extra keyword arguments passed to ``matplotlib.pyplot.savefig``.

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
        if ax is None:
            fig, ax = subplots(figsize=figsize, **fig_kwargs)
        else:
            fig = ax.figure

        # vertices
        if self.n > 0 and v_size > 0:
            scatter_kwargs = {"s": v_size, "c": v_color, "alpha": v_alpha}
            scatter_kwargs.update(v_kwargs)  # user overrides defaults
            ax.scatter(self.points[:, 0], self.points[:, 1], **scatter_kwargs)

        # boundary edges
        edges = self.graph.get_edgelist() if hasattr(self, "graph") else []
        if edges:
            segs = np.array(
                [[self.points[i], self.points[j]] for (i, j) in edges], dtype=float
            )
            line_kwargs = {"linewidths": e_size, "colors": e_color, "alpha": e_alpha}
            line_kwargs.update(e_kwargs)  # user overrides defaults
            lc = LineCollection(segs, **line_kwargs)
            ax.add_collection(lc)

        # title
        if title:
            plot_title = self.name
            if details and getattr(self, "details", None):
                plot_title += f"\n{self.details}"
            title_args = {"fontsize": fontsize}
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
            savefig_args = {"bbox_inches": "tight", "transparent": transparent}
            savefig_args.update(savefig_kwargs)
            fig.savefig(save + ".png", **savefig_args)
            fig.canvas.draw_idle()
            return fig, ax

    def __dist_nearest(self):
        if self.n == 0:
            return np.array([])
        i_indices = np.arange(self.n)
        if self.n <= self.__limit_vec:
            dist_matrix = cdist(self.points, self.points)
            dist_matrix[i_indices, i_indices] = np.inf
            dist_min = np.min(dist_matrix, axis=1)
        else:
            dist_min = np.empty(self.n)
            for i in range(self.n):
                diffs = self.points - self.points[i]
                dists_sq = np.sum(diffs**2, axis=1)
                dists_sq[i] = np.inf
                dist_min[i] = np.sqrt(np.min(dists_sq))
        return dist_min

    def _prepare_graphs_for_operation(self, other_graph_obj):
        graph_a_copy = self.graph.copy()
        graph_b_copy = other_graph_obj.graph.copy()
        for g_copy in [graph_a_copy, graph_b_copy]:
            if "name" not in g_copy.vertex_attributes():
                g_copy.vs["name"] = [f"v{i}" for i in range(g_copy.vcount())]
            attrs_to_delete = [
                attr for attr in g_copy.vertex_attributes() if attr != "name"
            ]
            for vattr in attrs_to_delete:
                del g_copy.vs[vattr]
        return graph_a_copy, graph_b_copy

    def _check_setpoints_compatibility(self, other):
        if not isinstance(other, GeometricGraph):
            raise TypeError("Input 'other' must be an instance of GeometricGraph.")
        if not (self.n == other.n and np.array_equal(self.points, other.points)):
            raise ValueError(
                "Graphs must be defined on the same point sets for this operation."
            )

    def union(self, other):
        self._check_setpoints_compatibility(other)
        graph_a, graph_b = self._prepare_graphs_for_operation(other)
        union_igraph = ig.union([graph_a, graph_b], byname=False)
        union_g = GeometricGraph(self.setpoints)
        union_g._GeometricGraph__graph = union_igraph
        union_g._GeometricGraph__m = union_igraph.ecount()
        union_g._GeometricGraph__add_lengths()
        union_g.name = f"Union of ({self.name}) and ({other.name})"
        union_g.details = "Union operation"
        return union_g

    def intersection(self, other):
        self._check_setpoints_compatibility(other)
        graph_a, graph_b = self._prepare_graphs_for_operation(other)
        intersection_igraph = ig.intersection([graph_a, graph_b], byname=False)
        intersection_g = GeometricGraph(self.setpoints)
        intersection_g._GeometricGraph__graph = intersection_igraph
        intersection_g._GeometricGraph__m = intersection_igraph.ecount()
        intersection_g._GeometricGraph__add_lengths()
        intersection_g.name = f"Intersection of ({self.name}) and ({other.name})"
        intersection_g.details = "Intersection operation"
        return intersection_g

    def difference(self, other):
        self._check_setpoints_compatibility(other)
        graph_a, graph_b = self._prepare_graphs_for_operation(other)
        difference_igraph = graph_a.difference(graph_b)
        difference_g = GeometricGraph(self.setpoints)
        difference_g._GeometricGraph__graph = difference_igraph
        difference_g._GeometricGraph__m = difference_igraph.ecount()
        difference_g._GeometricGraph__add_lengths()
        difference_g.name = f"Difference of ({self.name}) and ({other.name})"
        difference_g.details = "Difference operation (self - other)"
        return difference_g

    def symmetric_difference(self, other):
        self._check_setpoints_compatibility(other)
        edges_g = set(self.graph.get_edgelist())
        edges_h = set(other.graph.get_edgelist())
        sym_diff_edges = list(edges_g.symmetric_difference(edges_h))
        symmetric_g = GeometricGraph(self.setpoints)
        if sym_diff_edges:
            symmetric_g.graph.add_edges(sym_diff_edges)
        symmetric_g._GeometricGraph__m = symmetric_g.graph.ecount()
        symmetric_g._GeometricGraph__add_lengths()
        symmetric_g.name = f"Symmetric Difference of ({self.name}) and ({other.name})"
        symmetric_g.details = "Symmetric Difference operation"
        return symmetric_g

    def recovering(self, other, distance="R"):
        if not isinstance(other, GeometricGraph):
            raise TypeError("Input 'other' must be an instance of GeometricGraph.")
        union_graph = self.union(other)
        if distance == "R":
            symmetric_diff_graph = self.symmetric_difference(other)
            if union_graph.m == 0:
                return 0.0 if symmetric_diff_graph.m == 0 else 1.0
            return symmetric_diff_graph.m / union_graph.m
        else:
            raise NotImplementedError(f"Distance type '{distance}' is not supported.")

    def save(self, path, filename):
        self.__graph["name"] = self.name
        self.__graph["details"] = self.details
        if not path.endswith(("/", "\\")):
            path += "/"
        self.__graph.write_pickle(path + filename)
        np.save(path + filename + ".npy", self.points)
        del self.__graph["name"]
        del self.__graph["details"]

    def to_gpd_lines(self):
        GeoDataFrame, GeoSeries, LineString, _ = _require_gis_dependencies()

        if self.m == 0:
            return GeoDataFrame(columns=["union_initial", "union_final", "geometry"])

        if self.m > 0:
            _ = self.lengths
            _ = self.orientation

        point_coords = self.points

        if self.setpoints.dim != 2:
            raise ValueError(
                "Points must be a 2D array with shape (n, dim) where n"
                "is the number of points and dim is the dimension."
            )

        lines_geom = []
        edges = self.graph.get_edgelist()
        for u, v in edges:
            p1 = point_coords[u]
            p2 = point_coords[v]
            lines_geom.append(LineString([p1, p2]))
        gpd_lines = GeoDataFrame(geometry=GeoSeries(lines_geom))
        attr_names = self.graph.es.attribute_names()
        for attr_name in attr_names:
            gpd_lines[attr_name] = self.graph.es[attr_name]
        gpd_lines["union_initial"] = np.array(edges)[:, 0]
        gpd_lines["union_final"] = np.array(edges)[:, 1]
        final_columns = (
            ["union_initial", "union_final"]
            + [
                name
                for name in attr_names
                if name not in ["union_initial", "union_final"]
            ]
            + ["geometry"]
        )
        final_columns = [col for col in final_columns if col in gpd_lines.columns]
        return gpd_lines[final_columns]

    def to_gpd_polygons(self):
        GeoDataFrame, _, _, polygonize = _require_gis_dependencies()

        if self.setpoints.dim != 2:
            raise ValueError("Points must be a 2D array with shape (n, dim) ")
        if (self.cc - self.n + self.m) <= 0:
            raise TypeError(
                "The graph has no internal faces to polygonize "
                "(e.g., it's a tree or a line)."
            )
        gpd_lines = self.to_gpd_lines()
        if gpd_lines.empty:
            raise ValueError("Cannot create polygons from a graph with no edges.")
        polygons = list(polygonize(gpd_lines["geometry"]))
        if not polygons:
            raise ValueError(
                "Polygonization did not result in any polygons."
                "Ensure the graph forms closed regions."
            )
        return GeoDataFrame(geometry=polygons)


def load_graph(path, filename):
    points = np.load(path + filename + ".npy")
    graph = ig.Graph.Read_Pickle(path + filename)
    load_graph = GeometricGraph.from_graph(graph, points)
    load_graph.name = graph["name"]
    load_graph.details = graph["details"]
    del load_graph._GeometricGraph__graph["name"]
    del load_graph._GeometricGraph__graph["details"]
    return load_graph


def _unwrap_singleton(x):
    # unwrap (obj,) or [obj]
    if isinstance(x, (tuple, list)) and len(x) == 1:
        return x[0]
    return x


def draw_grid(
    graphs,
    nrows,
    ncols,
    *,
    figsize=None,
    constrained_layout=True,
    hide_unused=True,
    **draw_kwargs,
):
    """
    Draw a list of graph objects into an (nrows x ncols) matplotlib subplot grid.

    Parameters
    ----------
    graphs : list
        List of objects exposing .draw(ax=..., **draw_kwargs).
    nrows, ncols : int
        Grid shape.
    figsize : tuple or None
        Passed to plt.subplots.
    constrained_layout : bool
        Passed to plt.subplots.
    hide_unused : bool
        If graphs < nrows*ncols, hide remaining axes.
    draw_kwargs : dict
        Forwarded to each graph.draw(...).

    Returns
    -------
    (fig, axs)
    """

    fig, axs = subplots(
        nrows, ncols, figsize=figsize, constrained_layout=constrained_layout
    )

    axs_flat = axs.flat  # works for (nrows,ncols) and for 1D cases

    for ax, G in zip(axs_flat, graphs, strict=False):
        G = _unwrap_singleton(G)
        if not hasattr(G, "draw"):
            raise TypeError(
                f"Each item must have a .draw(...). Got {type(G)} after unwrapping."
            )
        G.draw(ax=ax, **draw_kwargs)

    if hide_unused:
        for ax in axs_flat:
            ax.set_visible(False)

    return fig, axs
