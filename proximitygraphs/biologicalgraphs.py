import contextlib

import numpy as np

from .geometricgraphs import GeometricGraph
from .points import SetPoints
from .proximitygraphs import DelaunayG

# ===========================================================
# BASE CLASS
# ===========================================================


class BiologicalGraph(GeometricGraph):
    """
    Base class for biologically-inspired adaptive or self-organizing networks.
    Extends GeometricGraph with the idea of dynamic evolution over time.
    """

    def __init__(self, setpoints):
        super().__init__(setpoints)
        self.name = "Biological Graph"
        self.details = "Base biological structure"

    def evolve(self, steps=100):
        raise NotImplementedError("Subclasses must implement evolve()")


# ------------------------------------------------------------------
# PhysarumGraph
# ------------------------------------------------------------------
class PhysarumGraph(BiologicalGraph):
    """
    Physarum-like adaptive network (Tero et al. 2010) with:
    - Multiple sources/sinks
    - Automatic reconnection if fragmented
    - Optional base graphs: 'delaunay' or 'complete'
    """

    def __init__(
        self,
        setpoints,
        sources=None,
        dt=0.1,
        gamma=1.5,
        eps=1e-3,
        steps=200,
        base_graph="delaunay",
        reconnect=True,
    ):
        if not isinstance(setpoints, SetPoints):
            raise TypeError("setpoints must be a SetPoints instance.")
        super().__init__(setpoints)

        self.name = "Physarum Graph"
        self.details = f"γ={gamma}, dt={dt}, base={base_graph}, reconnect={reconnect}"
        self.reconnect = reconnect

        if base_graph == "delaunay":
            base = DelaunayG(setpoints)
        elif base_graph == "complete":
            base = GeometricGraph.complete(setpoints)
        else:
            raise ValueError("base_graph must be 'delaunay' or 'complete'.")

        self._GeometricGraph__graph = base.graph.copy()
        self._GeometricGraph__size()
        self._GeometricGraph__add_lengths()

        m = self.graph.ecount()
        self.graph.es["D"] = np.ones(m) * 0.1
        self.graph.es["Q"] = np.zeros(m)

        self.dt = float(dt)
        self.gamma = float(gamma)
        self.eps = float(eps)

        n = self.n
        if sources is None:
            sources = [0]

        self.sources = [int(i) for i in sources if 0 <= i < n]
        self.sinks = [i for i in range(n) if i not in self.sources]

        if not self.sources or not self.sinks:
            raise ValueError("At least one valid source required.")

        self.evolve(steps)

    # ------------------------------------------------------------------
    def evolve(self, steps=100):
        """Run dynamic adaptation of conductivities for a given number of steps."""
        for _ in range(int(steps)):
            with contextlib.suppress(np.linalg.LinAlgError):
                self._update_step()

            if self.reconnect:
                comps = self.graph.components()
                if len(comps) > 1:
                    self._reconnect_components()

        weak = [e.index for e in self.graph.es if float(e["D"]) < self.eps]
        if weak:
            self.graph.delete_edges(weak)
        self._GeometricGraph__size()
        self._GeometricGraph__add_lengths()

    # ------------------------------------------------------------------
    def _update_step(self):
        """One Physarum update step with multiple sources/sinks."""
        n = self.n
        edges = np.array(self.graph.get_edgelist())
        D = np.array(self.graph.es["D"], dtype=float)
        L = np.array(self.graph.es["dist_eucl"], dtype=float)
        L_safe = np.where(L <= 0, 1e-8, L)

        # Build Laplacian-like conductance matrix
        A = np.zeros((n, n), dtype=float)
        for (i, j), Dij, Lij in zip(edges, D, L_safe, strict=False):
            c = Dij / Lij
            A[i, i] += c
            A[j, j] += c
            A[i, j] -= c
            A[j, i] -= c

        b = np.zeros(n, dtype=float)
        if self.sources:
            for s in self.sources:
                b[s] = 1.0 / len(self.sources)
        if self.sinks:
            for t in self.sinks:
                b[t] = -1.0 / len(self.sinks)

        reg = 1e-8
        try:
            p = np.linalg.solve(A + np.eye(n) * reg, b)
        except np.linalg.LinAlgError:
            p, *_ = np.linalg.lstsq(A + np.eye(n) * 1e-6, b, rcond=None)

        Q = D * (p[edges[:, 0]] - p[edges[:, 1]]) / L_safe
        D_new = D + self.dt * (np.abs(Q) ** self.gamma - D)

        D_new = np.maximum(D_new, 1e-5)

        self.graph.es["Q"] = Q.tolist()
        self.graph.es["D"] = D_new.tolist()

    # ------------------------------------------------------------------
    def _reconnect_components(self):
        """If the graph becomes fragmented, reconnect using nearest points."""
        comps = self.graph.components()
        if len(comps) <= 1:
            return
        centroids = []
        for comp in comps:
            pts = np.array([self.setpoints.coords[i] for i in comp])
            centroids.append(pts.mean(axis=0))
        centroids = np.array(centroids)

        dist_matrix = np.linalg.norm(
            centroids[:, None, :] - centroids[None, :, :], axis=2
        )
        i, j = np.unravel_index(
            np.argmin(dist_matrix + np.eye(len(centroids)) * 1e9), dist_matrix.shape
        )

        comp_i = comps[i]
        comp_j = comps[j]
        min_dist = np.inf
        best_pair = None
        for u in comp_i:
            for v in comp_j:
                d = np.linalg.norm(self.setpoints.coords[u] - self.setpoints.coords[v])
                if d < min_dist:
                    min_dist = d
                    best_pair = (u, v)

        if best_pair and not self.graph.are_connected(*best_pair):
            self.graph.add_edge(*best_pair)
            self.graph.es[-1]["D"] = 0.05
            self.graph.es[-1]["Q"] = 0.0
            self.graph.es[-1]["dist_eucl"] = float(min_dist)
            self._GeometricGraph__size()


# ------------------------------------------------------------------
# FungalGraph


class FungalGraph(BiologicalGraph):
    """
    Fungal network constructed using a bio-inspired expansion metaheuristic.

    This class mimics the growth pattern of fungal networks (like Physarum polycephalum)
    to create efficient, connected networks that:
    - Prioritize short edges for efficiency
    - Find shortest paths between node pairs
    - Guarantee a single connected component
    - Avoid star topologies through degree control
    - Balance between cost and redundancy

    The algorithm starts with a tree backbone and iteratively
    adds edges based on a multi-objective benefit function that considers:
    1. Edge length (shorter is better)
    2. Degree balance (avoid high-degree hubs)
    3. Path improvement (create useful shortcuts)

    Attributes
    ----------
    name : str
        Name of the graph type
    details : str
        Description of parameters used
    max_degree : int
        Maximum degree allowed per vertex
    """

    def __init__(
        self,
        setpoints,
        max_degree=6,
        distance_threshold_percentile=75,
        growth_iterations=100,
        prune_weak_factor=0.3,
        sources=None,
        dt=0.1,
        gamma=1.5,
        eps=1e-3,
        steps=200,
        seed=None,
    ):
        """
        Initialize a FungalGraph through bio-inspired expansion.

        Parameters
        ----------
        setpoints : SetPoints
            The set of points to connect
        max_degree : int, optional
            Maximum degree allowed per vertex to avoid star topologies (default: 6)
        distance_threshold_percentile : float, optional
            Only consider edges below this percentile of all distances (default: 75)
        growth_iterations : int, optional
            Number of growth iterations to expand the network (default: 100)
        prune_weak_factor : float, optional
            Fraction of weakest edges to prune after growth, in [0,1] (default: 0.3)
        seed : int, optional
            Random seed for reproducibility


        """
        if not isinstance(setpoints, SetPoints):
            raise TypeError("setpoints must be a SetPoints instance.")

        super().__init__(setpoints)

        self.name = "Fungal Graph"
        self.details = f"max_deg={max_degree}, thresh={distance_threshold_percentile}%, prune={prune_weak_factor}"
        self.max_degree = max_degree

        self.sources = sources if sources is not None else [0]
        self.dt = float(dt)
        self.gamma = float(gamma)
        self.eps = float(eps)
        self.steps = int(steps)

        # Initialize with growth
        self._initialize_network(
            distance_threshold_percentile=distance_threshold_percentile,
            growth_iterations=growth_iterations,
            prune_weak_factor=prune_weak_factor,
            seed=seed,
        )

    def _initialize_network(
        self, distance_threshold_percentile, growth_iterations, prune_weak_factor, seed
    ):
        """Construct the fungal network using bio-inspired growth."""
        n = self.n
        if n < 2:
            return

        rng = np.random.default_rng(seed)

        from scipy.spatial.distance import pdist, squareform

        coords = self.setpoints.points
        dist_condensed = pdist(coords)
        dist_matrix = squareform(dist_condensed)

        base = PhysarumGraph(
            self.setpoints,
            self.sources,
            dt=self.dt,
            gamma=self.gamma,
            eps=self.eps,
            steps=self.steps,
            base_graph="delaunay",
            reconnect=True,
        )
        base_edges = base.graph.get_edgelist()
        self.graph.add_edges(base_edges)

        for e in self.graph.es:
            i, j = e.tuple
            self.graph.es[e.index]["dist_eucl"] = float(dist_matrix[i, j])

        self._GeometricGraph__size()

        threshold_dist = np.percentile(dist_condensed, distance_threshold_percentile)

        candidate_edges = []
        for i in range(n):
            for j in range(i + 1, n):
                if dist_matrix[i, j] <= threshold_dist:
                    if not self.graph.are_connected(i, j):
                        candidate_edges.append((i, j, dist_matrix[i, j]))

        candidate_edges.sort(key=lambda x: x[2])

        for _iteration in range(growth_iterations):
            if not candidate_edges:
                break

            degrees = np.array(self.graph.degree())
            edges_added = []

            for i, j, dist in candidate_edges[:]:
                # Check degree constraints
                if degrees[i] >= self.max_degree or degrees[j] >= self.max_degree:
                    continue

                dist_score = 1.0 / (dist + 1e-6)

                degree_balance = 1.0 / (1.0 + abs(degrees[i] - degrees[j]))

                try:
                    path = self.graph.get_shortest_paths(i, j)[0]
                    current_path_length = len(path) - 1
                    shortcut_benefit = max(0, current_path_length - 1) / n
                except:
                    shortcut_benefit = 1.0  # Not connected yet

                benefit = (
                    0.4 * dist_score + 0.3 * degree_balance + 0.3 * shortcut_benefit
                )

                if rng.random() < benefit * 0.5:
                    self.graph.add_edge(i, j)
                    self.graph.es[-1]["dist_eucl"] = float(dist)

                    degrees[i] += 1
                    degrees[j] += 1
                    edges_added.append((i, j, dist))

            for edge in edges_added:
                if edge in candidate_edges:
                    candidate_edges.remove(edge)

            self._GeometricGraph__size()

            if self.m > len(base_edges) * 3:
                break

        while self.cc > 1:
            comps = self.graph.components()
            min_dist = np.inf
            best_pair = None

            for ci in range(len(comps)):
                for cj in range(ci + 1, len(comps)):
                    for u in comps[ci]:
                        for v in comps[cj]:
                            d = dist_matrix[u, v]
                            if d < min_dist:
                                min_dist = d
                                best_pair = (u, v)

            if best_pair:
                self.graph.add_edge(*best_pair)
                self.graph.es[-1]["dist_eucl"] = float(min_dist)
            else:
                break

        self._GeometricGraph__size()

        if prune_weak_factor > 0 and self.m > len(base_edges):
            betweenness = np.array(self.graph.edge_betweenness())

            edges_to_keep = set(range(len(base_edges)))

            non_base_edges = [
                (i, betweenness[i]) for i in range(len(base_edges), self.graph.ecount())
            ]
            non_base_edges.sort(key=lambda x: x[1], reverse=True)

            n_to_keep = int(len(non_base_edges) * (1 - prune_weak_factor))
            for i in range(min(n_to_keep, len(non_base_edges))):
                edges_to_keep.add(non_base_edges[i][0])

            edges_to_delete = [
                i for i in range(self.graph.ecount()) if i not in edges_to_keep
            ]
            if edges_to_delete:
                self.graph.delete_edges(edges_to_delete)

            self._GeometricGraph__size()

        # Final update
        self._GeometricGraph__add_lengths()

    def evolve(self, steps=100):
        """
        Placeholder for evolution method (required by BiologicalGraph).

        FungalGraph uses a constructive approach rather than iterative evolution,
        so this method does nothing.
        """
        pass
