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


# ------------------------------------------------------------------
# AntColonyGraph: adapted to private attributes
# ------------------------------------------------------------------
class AntColonyGraph(BiologicalGraph):
    """
    Ant Colony inspired adaptive graph. Edges carry 'pheromone' attribute.
    """

    def __init__(self, setpoints, n_ants=10, alpha=1.0, beta=2.0,
                 rho=0.1, Q=1.0, steps=100, base_graph="delaunay"):
        if not isinstance(setpoints, SetPoints):
            raise TypeError("setpoints must be a SetPoints instance.")
        super().__init__(setpoints)
        self.name = "Ant Colony Graph"
        self.details = f"α={alpha}, β={beta}, ρ={rho}, base={base_graph}"

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
        if m == 0:
            return

        self.graph.es["pheromone"] = np.ones(m) * 0.1
        self.alpha = float(alpha)
        self.beta = float(beta)
        self.rho = float(rho)
        self.Q = float(Q)
        self.n_ants = int(n_ants)

        self.evolve(steps)

    def evolve(self, steps=100):
        for _ in range(int(steps)):
            self._simulate_ants()
            self._evaporate_pheromones()

    def _simulate_ants(self):
        n = self.n
        edges = np.array(self.graph.get_edgelist())
        pher = np.array(self.graph.es["pheromone"], dtype=float)
        length = np.array(self.graph.es["dist_eucl"], dtype=float)

        
        incident = [[] for _ in range(n)]
        for idx, (u, v) in enumerate(edges):
            incident[u].append(idx)
            incident[v].append(idx)

        for _ in range(self.n_ants):
            current = np.random.randint(0, n)
            visited = {current}
            path_edges = []

            # perform at most n-1 steps
            for _step in range(n - 1):
                possible = incident[current]
                if not possible:
                    break
                
                pher_vals = pher[possible]
                length_vals = length[possible]
                heuristic = 1.0 / (length_vals + 1e-8)
                probs = (pher_vals ** self.alpha) * (heuristic ** self.beta)
                total = probs.sum()
                if total <= 0 or np.isnan(total):
                    break
                probs = probs / total
                chosen_local = np.random.choice(len(possible), p=probs)
                chosen_edge_idx = possible[chosen_local]
                path_edges.append(chosen_edge_idx)

                
                u, v = edges[chosen_edge_idx]
                next_node = v if u == current else u
                if next_node in visited:
                    
                    break
                visited.add(next_node)
                current = next_node

            if len(path_edges) > 0:
                L_path = float(sum(length[e] for e in path_edges))
                if L_path <= 0:
                    continue
                delta = self.Q / L_path
                for e in path_edges:
                    pher[e] += delta

        
        self.graph.es["pheromone"] = pher.tolist()

    def _evaporate_pheromones(self):
        pher = np.array(self.graph.es["pheromone"], dtype=float)
        pher *= (1.0 - self.rho)
        
        pher = np.maximum(pher, 1e-12)
        self.graph.es["pheromone"] = pher.tolist()
        
    def _normalize_pheromones(self, clip=True):
        """Normalize pheromone values to [0,1] range for stable visualization."""
        pher = np.array(self.graph.es["pheromone"], dtype=float)
        
        pher = np.maximum(pher, 1e-10)
        
        pher_log = np.log1p(pher)
        pher_norm = (pher_log - pher_log.min()) / (pher_log.max() - pher_log.min() + 1e-12)
        if clip:
            pher_norm = np.clip(pher_norm, 0, 1)
        self.graph.es["pheromone_norm"] = pher_norm.tolist()
        return pher_norm