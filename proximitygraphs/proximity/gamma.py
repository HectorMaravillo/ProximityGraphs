"""Gamma-neighborhood graph construction.

This module implements the two-parameter gamma-neighborhood graph introduced
by Veltkamp (1992). Given a finite planar point set, two sites p and q are
connected when at least one gamma-neighborhood N_{gamma0,gamma1}(p, q) is
empty of all other sites.

The gamma-neighborhood graph is an empty-region proximity graph family that
unifies several classical geometric graphs, including the convex hull,
Delaunay triangulation, Gabriel graph, circle-based beta-skeleton, void graph,
and complete graph.

This implementation handles special half-plane limit cases explicitly, uses
Delaunay candidate pruning only in a safe planar finite-radius regime, and
keeps a vectorized all-points verifier as the correctness fallback.

References
----------
Veltkamp, R. C. (1992). The gamma-neighborhood graph. Computational Geometry,
1(4), 227-246. doi:10.1016/0925-7721(92)90003-B
"""

from itertools import combinations

import numpy as np
from igraph import Graph
from scipy.spatial import Delaunay, QhullError, cKDTree

from .base import ProximityGraph
from .hull import Convex_Hull


class Gamma_Graph(ProximityGraph):
    """
    Constructs the gamma-Neighborhood Graph as defined by Veltkamp (1992).

    Two points p and q are connected if at least one gamma-neighborhood
    N_{gamma0,gamma1}(p, q) is empty of all other sites.

    Parameters
    ----------
    setpoints : SetPoints
        The set of points.
    gamma0 : float
        First gamma parameter, in [-1, 1].
    gamma1 : float
        Second gamma parameter, in [-1, 1], with |gamma0| <= |gamma1|.
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
        self.name = "gamma-Neighborhood Graph"
        self.details = f"gamma0={gamma0}, gamma1={gamma1}, closed={closed}"
        self.__gamma0 = float(gamma0)
        self.__gamma1 = float(gamma1)
        self.__inequality = self._ProximityGraph__closed_region(closed)
        self.__block_size = int(block_size)
        self.__planar_fast_ok = False

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

        # ---- Generic finite-radius case (no |gamma| = 1) ----
        pairs = self.__defined_pairs()
        # Only replace the all-points scan in the theorem-safe planar regime.
        # Otherwise the existing vectorized verifier remains the correctness
        # fallback.
        if self.__can_use_planar_fast_gamma():
            self.__assign_edges_planar_fast(pairs)
        else:
            self.__assign_edges(pairs)  # uses self.__block_size

        self.graph.simplify()
        self._GeometricGraph__size()
        self._GeometricGraph__add_lengths()

    @classmethod
    def from_graph(
        cls, geom_graph, gamma0=0.0, gamma1=0.0, closed=False, block_size=512
    ):
        """
        Build a gamma-Neighborhood Graph on top of an existing GeometricGraph.

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

        g.name = "gamma-Neighborhood Graph"
        g.details = f"gamma0={gamma0}, gamma1={gamma1}, closed={closed}, (from graph)"
        g._GeometricGraph__setpoints = geom_graph.setpoints
        g._GeometricGraph__graph = Graph()
        g._GeometricGraph__graph.add_vertices(geom_graph.n)

        g.__gamma0 = float(gamma0)
        g.__gamma1 = float(gamma1)
        g.__inequality = g._ProximityGraph__closed_region(closed)
        g.__block_size = int(block_size)
        planar_delaunay_pairs = g.__safe_planar_delaunay_pairs()
        g.__planar_fast_ok = planar_delaunay_pairs is not None

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
        if g.__planar_fast_ok:
            delaunay_edge_set = {
                tuple(edge) for edge in map(tuple, planar_delaunay_pairs.tolist())
            }
            g.__planar_fast_ok = all(
                tuple(sorted(map(int, edge))) in delaunay_edge_set
                for edge in candidate_pairs
            )
        # The fast planar branch is only used when the Delaunay-subgraph
        # assumptions are safely satisfied; otherwise keep the current
        # blockwise verifier as the source of correctness.
        if g.__can_use_planar_fast_gamma():
            g.__assign_edges_planar_fast(candidate_pairs)
        else:
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
        - Otherwise (finite radii, gamma1>=0) the gamma-graph is a DT subgraph
          -> use DT edges.
        """
        g0, g1 = self.__gamma0, self.__gamma1
        dim = self.points.shape[1]
        self.__planar_fast_ok = False

        # special/unsafe ranges -> all pairs
        if abs(g0) == 1.0 or abs(g1) == 1.0 or g1 < 0.0:
            return np.array(list(combinations(range(self.n), 2)), dtype=int)

        # not enough points for DT
        if self.n < dim + 1:
            return np.array(list(combinations(range(self.n), 2)), dtype=int)

        # DT candidates
        pairs = self.__safe_planar_delaunay_pairs()
        if pairs is None:
            return np.array(list(combinations(range(self.n), 2)), dtype=int)

        self.__planar_fast_ok = True
        return pairs

    def __safe_planar_delaunay_pairs(self):
        """
        Return planar Delaunay edges when the 2D subgraph regime is safe.

        Any uncertainty falls back to ``None`` so the existing brute-force
        verifier remains responsible for correctness.
        """
        if self.points.shape[1] != 2 or self.n < 3:
            return None

        if not np.isfinite(self.points).all():
            return None

        if np.unique(self.points, axis=0).shape[0] != self.n:
            return None

        try:
            delaunay = Delaunay(self.points)
        except (QhullError, ValueError):
            return None

        simplices = np.asarray(delaunay.simplices, dtype=int)
        if simplices.ndim != 2 or simplices.shape[1] != 3 or simplices.size == 0:
            return None

        edges = set()
        for tri in simplices:
            a, b, c = map(int, tri)
            edges.add(tuple(sorted((a, b))))
            edges.add(tuple(sorted((b, c))))
            edges.add(tuple(sorted((a, c))))

        if not edges:
            return None

        return np.array(sorted(edges), dtype=int)

    def __can_use_planar_fast_gamma(self):
        """
        The fast path is only valid in the safe planar Delaunay-subgraph regime.

        This keeps the optimization inside the requested gamma1 window while
        routing degenerate or half-plane-limit cases back to the existing
        verifier.
        """
        g0, g1 = self.__gamma0, self.__gamma1
        if not (0.0 <= g1 <= 1.0):
            return False

        if abs(g0) == 1.0 or abs(g1) == 1.0:
            return False

        return self.__planar_fast_ok

    def __assign_edges_planar_fast(self, pairs):
        """
        Exact emptiness test for the safe planar regime using local KD-tree queries.

        On planar Delaunay candidates this avoids the fallback's global all-points
        scan while preserving the current neighborhood and boundary semantics.
        """
        if self.n < 2 or pairs.size == 0:
            return

        pts = self.points
        tree = cKDTree(pts)

        g0, g1 = self.__gamma0, self.__gamma1

        closed = self.__inequality(0.0, 0.0)  # True iff <= is used
        if closed:

            def comp(dist2, R2):
                return dist2 <= R2
        else:

            def comp(dist2, R2):
                return dist2 < R2

        intersection_mode = g1 <= 0.0
        edges_out = []

        for i, j in pairs:
            p = pts[i]
            q = pts[j]
            v = q - p

            d2 = float(np.dot(v, v))
            if d2 <= 0.0:
                continue

            d = np.sqrt(d2)
            r = d / 2.0
            r2 = d2 / 4.0

            nvec = np.array([-v[1], v[0]], dtype=float) / d
            m_mid = (p + q) / 2.0

            R0 = r / (1.0 - abs(g0))
            R1 = r / (1.0 - abs(g1))
            R0_2 = R0 * R0
            R1_2 = R1 * R1

            s0 = np.sqrt(max(R0_2 - r2, 0.0))
            s1 = np.sqrt(max(R1_2 - r2, 0.0))

            c0_up = m_mid + s0 * nvec
            c0_dn = m_mid - s0 * nvec
            c1_up = m_mid + s1 * nvec
            c1_dn = m_mid - s1 * nvec

            if g0 != 0.0 and g1 != 0.0:
                if g0 * g1 > 0.0:
                    neighborhoods = ((c0_up, c1_dn), (c0_dn, c1_up))
                else:
                    neighborhoods = ((c0_up, c1_up), (c0_dn, c1_dn))
            else:
                neighborhoods = ((c0_up, c1_up),)

            empty_any = False
            for c_a, c_b in neighborhoods:
                candidates = set(tree.query_ball_point(c_a, R0))
                candidates.update(tree.query_ball_point(c_b, R1))
                candidates.discard(int(i))
                candidates.discard(int(j))

                if not candidates:
                    empty_any = True
                    break

                idx = np.fromiter(candidates, dtype=int)
                test_points = pts[idx]

                dist_a2 = np.einsum("ij,ij->i", test_points - c_a, test_points - c_a)
                dist_b2 = np.einsum("ij,ij->i", test_points - c_b, test_points - c_b)

                in_a = comp(dist_a2, R0_2)
                in_b = comp(dist_b2, R1_2)
                inside = (in_a & in_b) if intersection_mode else (in_a | in_b)

                if not np.any(inside):
                    empty_any = True
                    break

            if empty_any:
                edges_out.append((int(i), int(j)))

        if edges_out:
            self.graph.add_edges(edges_out)

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
