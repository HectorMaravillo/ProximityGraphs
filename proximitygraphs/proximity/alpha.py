"""Alpha-shape and alpha-hull construction.

This module implements alpha-shape and alpha-hull boundary extraction for
finite planar point sets. Alpha-shapes describe the geometric shape of a point
cloud at a chosen scale by filtering Delaunay simplices with radius criteria;
alpha-hulls provide a related boundary representation based on circular arcs.

These constructions are part of computational morphology and are useful for
recovering non-convex shape from scattered data.

References
----------
Edelsbrunner, H., Kirkpatrick, D., & Seidel, R. (1983). On the shape of a set
of points in the plane. IEEE Transactions on Information Theory, 29(4),
551-559.

Radke, J. D. (1988). On the shape of a set of points. In Computational
Morphology: A Computational Geometric Approach to the Analysis of Form,
105-136. Elsevier Science.
"""

from collections import Counter, defaultdict

import numpy as np
from scipy.spatial import ConvexHull, Delaunay

from .base import ProximityGraph


class Alpha_Shape(ProximityGraph):
    """
    Constructs the alpha-Shape boundary of a planar point set.

    Two vertices i and j are connected iff edge (i, j) lies on the
    boundary of triangles whose circumradius R satisfies
    ``R <= 1/|alpha| + tol``. For ``alpha ≈ 0`` the boundary reduces to the
    convex hull. For ``alpha > 0`` the furthest-site Delaunay variant is used.

    Attributes
    ----------
    name : str
        Graph name, set to ``"Alpha-Shape"``.
    details : str
        Short descriptor with the chosen alpha, e.g., ``"alpha=2.0"``.
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
          * ``n == 2`` and ``alpha ≈ 0``: single edge.
          * ``alpha ≈ 0`` and ``n >= 3``: convex hull edges.
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

        if n == 0 or n == 1:
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
                    keep = (R_alpha + tol) >= R
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
    Constructs the alpha-Hull of a planar point set.

    For ``alpha ≈ 0`` the object reduces to the convex hull rendered as straight
    segments. For ``alpha ≠ 0`` it reuses the alpha-shape boundary and replaces each
    boundary edge by a circular arc of radius ``R = 1/|alpha|`` consistent with the
    interior/exterior choice implied by ``sign(alpha)`` and the boundary orientation.
    The geometric graph stores straight segments for analytics, while sampled
    arc points are kept in ``self.arcs`` for rendering.

    Attributes
    ----------
    name : str
        Graph name, set to ``"Alpha-Hull"``.
    details : str
        Short descriptor with alpha, e.g., ``"alpha=1.5"``.
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
      1) If ``alpha ≈ 0`` use convex hull edges.
      2) Else build ``Alpha_Shape`` with the same ``alpha`` to get boundary cycles.
      3) For each boundary edge ``(p, q)`` compute candidate circle centers of
         radius ``R = 1/|alpha|`` through ``p`` and ``q``.
      4) Select the center whose arc is interior if ``alpha > 0`` and exterior if
         ``alpha < 0``, based on polygon signed area and local orientation tests.
      5) Sample the minor arc between ``p`` and ``q`` and store in ``arcs``.
      6) Insert ``(i, j)`` as a straight edge into ``graph`` for analytics.

    See Also
    --------
    Alpha_Shape : Boundary extractor used to seed alpha-Hull construction.
    scipy.spatial.ConvexHull : Hull used when ``alpha ≈ 0``.
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
            alpha parameter. For ``alpha ≈ 0`` the convex hull is used. For
            ``alpha ≠ 0`` the circular-arc hull uses radius ``R = 1/|alpha|``.
        n_points_per_arc : int, optional
            Number of samples along each minor arc between its endpoints.
            Default is 40.
        tol : float, optional
            Tolerance forwarded to the internal alpha-shape filtering. Default 1e-12.
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
            # reuse alpha-shape boundary cycles
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
        Plots the alpha-Hull with circular arcs.

        Parameters
        ----------
        figsize : tuple of (float, float), optional
            Figure size in inches. Default (6, 6).
        v_size : float, optional
            Marker size for vertices. 0 disables vertex scatter. Default 3.
        v_color : str, optional
            Vertex color passed to Matplotlib. Default "#00072D".
        v_alpha : float, optional
            Vertex alpha level between 0 (transparent) and 1 (opaque).
            Default 1.
        e_size : float, optional
            Line width for arcs. Default 1.
        e_color : str, optional
            Color for arcs. Default "#0A2472".
        e_alpha : float, optional
            Arc alpha level between 0 (transparent) and 1 (opaque).
            Default 1.
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
            scatter_kwargs = {"s": v_size, "c": v_color, "alpha": v_alpha}
            scatter_kwargs.update(v_kwargs)  # user overrides defaults
            ax.scatter(self.points[:, 0], self.points[:, 1], **scatter_kwargs)

        # arcs (same "edges" slot, but drawn as curves)
        arcs = getattr(self, "arcs", None)
        if arcs:
            line_kwargs = {"linewidth": e_size, "color": e_color, "alpha": e_alpha}
            line_kwargs.update(e_kwargs)  # user overrides defaults
            for arc in arcs:
                # arc expected shape (m, 2)
                ax.plot(arc[:, 0], arc[:, 1], **line_kwargs)

        # title
        if title:
            plot_title = getattr(self, "name", self.__class__.__name__)
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
        ``Deltatheta ∈ (-pi, pi]``.

        """
        cp = p - center
        cq = q - center
        th1 = np.arctan2(cp[1], cp[0])
        th2 = np.arctan2(cq[1], cq[0])
        dtheta = (th2 - th1 + np.pi) % (2 * np.pi) - np.pi
        thetas = th1 + np.linspace(0.0, 1.0, n_points) * dtheta
        return center + np.column_stack([np.cos(thetas), np.sin(thetas)]) * radius
