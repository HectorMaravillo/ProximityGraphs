from .points import SetPoints
from .geometricgraphs import GeometricGraph
from .geometricgraphs import load_graph

import numpy as np
import igraph as ig
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
# PhysarumGraph: corrected to use the internal attributes of GeometricGraph
# ------------------------------------------------------------------
class PhysarumGraph(BiologicalGraph):
    """
    Physarum-like adaptive network (Tero et al. 2010) with:
    - Multiple sources/sinks
    - Automatic reconnection if fragmented
    - Optional base graphs: 'delaunay' or 'complete'
    """

    def __init__(self, setpoints, sources=None, sinks=None,
                 dt=0.1, gamma=1.5, eps=1e-3, steps=200,
                 base_graph="delaunay", reconnect=True):
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
            raise ValueError("base_graph must be 'delaunay' or 'complete'")

        
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
        if sinks is None:
            sinks = [min(1, n - 1)]
        self.sources = [int(i) for i in sources if 0 <= i < n]
        self.sinks = [int(i) for i in sinks if 0 <= i < n]

        if not self.sources or not self.sinks:
            raise ValueError("At least one valid source and sink required.")

        
        self.evolve(steps)

    # ------------------------------------------------------------------
    def evolve(self, steps=100):
        """Run dynamic adaptation of conductivities for a given number of steps."""
        for _ in range(int(steps)):
            try:
                self._update_step()
            except np.linalg.LinAlgError:
                pass  

            
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
        for (i, j), Dij, Lij in zip(edges, D, L_safe):
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
        D_new = D + self.dt * (np.abs(Q)**self.gamma - D)

        
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

        
        dist_matrix = np.linalg.norm(centroids[:, None, :] - centroids[None, :, :], axis=2)
        i, j = np.unravel_index(np.argmin(dist_matrix + np.eye(len(centroids)) * 1e9), dist_matrix.shape)

        
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


