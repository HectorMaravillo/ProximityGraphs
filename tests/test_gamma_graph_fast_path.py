"""Focused coverage for the conservative Gamma_Graph planar fast path."""

from unittest.mock import patch

import numpy as np

import proximitygraphs as pg

FAST_METHOD = "_Gamma_Graph__assign_edges_planar_fast"
FALLBACK_METHOD = "_Gamma_Graph__assign_edges"
CAN_USE_METHOD = "_Gamma_Graph__can_use_planar_fast_gamma"


def _edge_list(graph):
    return sorted(graph.graph.get_edgelist())


def test_gamma_graph_planar_fast_path_matches_fallback():
    points = pg.SetPoints.uniform_square(n=24, seed=1234)

    calls = {"fast": 0}
    original_fast = getattr(pg.Gamma_Graph, FAST_METHOD)

    def tracked_fast(self, pairs):
        calls["fast"] += 1
        return original_fast(self, pairs)

    with patch.object(pg.Gamma_Graph, FAST_METHOD, new=tracked_fast):
        fast_graph = pg.Gamma_Graph(
            points, gamma0=0.25, gamma1=0.75, closed=False, block_size=16
        )

    with patch.object(pg.Gamma_Graph, CAN_USE_METHOD, return_value=False):
        fallback_graph = pg.Gamma_Graph(
            points, gamma0=0.25, gamma1=0.75, closed=False, block_size=16
        )

    assert calls["fast"] == 1
    assert _edge_list(fast_graph) == _edge_list(fallback_graph)


def test_gamma_graph_from_graph_planar_fast_path_matches_fallback():
    points = pg.SetPoints.uniform_square(n=24, seed=4321)
    base_graph = pg.DelaunayG(points)

    calls = {"fast": 0}
    original_fast = getattr(pg.Gamma_Graph, FAST_METHOD)

    def tracked_fast(self, pairs):
        calls["fast"] += 1
        return original_fast(self, pairs)

    with patch.object(pg.Gamma_Graph, FAST_METHOD, new=tracked_fast):
        fast_graph = pg.Gamma_Graph.from_graph(
            base_graph, gamma0=0.25, gamma1=0.75, closed=False, block_size=16
        )

    with patch.object(pg.Gamma_Graph, CAN_USE_METHOD, return_value=False):
        fallback_graph = pg.Gamma_Graph.from_graph(
            base_graph, gamma0=0.25, gamma1=0.75, closed=False, block_size=16
        )

    assert calls["fast"] == 1
    assert _edge_list(fast_graph) == _edge_list(fallback_graph)


def test_gamma_graph_negative_gamma1_uses_fallback():
    points = pg.SetPoints.uniform_square(n=18, seed=2026)

    calls = {"fast": 0, "fallback": 0}
    original_fast = getattr(pg.Gamma_Graph, FAST_METHOD)
    original_fallback = getattr(pg.Gamma_Graph, FALLBACK_METHOD)

    def tracked_fast(self, pairs):
        calls["fast"] += 1
        return original_fast(self, pairs)

    def tracked_fallback(self, pairs):
        calls["fallback"] += 1
        return original_fallback(self, pairs)

    with (
        patch.object(pg.Gamma_Graph, FAST_METHOD, new=tracked_fast),
        patch.object(pg.Gamma_Graph, FALLBACK_METHOD, new=tracked_fallback),
    ):
        pg.Gamma_Graph(points, gamma0=-0.25, gamma1=-0.75, closed=False)

    assert calls["fast"] == 0
    assert calls["fallback"] == 1


def test_gamma_graph_special_cases_remain_unchanged():
    points = pg.SetPoints.grid(shape=(2, 2))

    convex_hull_edges = _edge_list(pg.Convex_Hull(points))

    assert pg.Gamma_Graph(points, gamma0=1.0, gamma1=1.0).m == 0
    assert pg.Gamma_Graph(points, gamma0=-1.0, gamma1=-1.0).m == 6
    assert (
        _edge_list(pg.Gamma_Graph(points, gamma0=-1.0, gamma1=1.0)) == convex_hull_edges
    )
    assert (
        _edge_list(pg.Gamma_Graph(points, gamma0=1.0, gamma1=-1.0)) == convex_hull_edges
    )


def test_gamma_graph_degenerate_planar_input_falls_back_cleanly():
    points = pg.SetPoints(
        np.array(
            [
                [0.0, 0.0],
                [1.0, 0.0],
                [2.0, 0.0],
                [3.0, 0.0],
            ]
        )
    )

    calls = {"fast": 0, "fallback": 0}
    original_fast = getattr(pg.Gamma_Graph, FAST_METHOD)
    original_fallback = getattr(pg.Gamma_Graph, FALLBACK_METHOD)

    def tracked_fast(self, pairs):
        calls["fast"] += 1
        return original_fast(self, pairs)

    def tracked_fallback(self, pairs):
        calls["fallback"] += 1
        return original_fallback(self, pairs)

    with (
        patch.object(pg.Gamma_Graph, FAST_METHOD, new=tracked_fast),
        patch.object(pg.Gamma_Graph, FALLBACK_METHOD, new=tracked_fallback),
    ):
        graph = pg.Gamma_Graph(points, gamma0=0.25, gamma1=0.5, closed=False)

    with patch.object(pg.Gamma_Graph, CAN_USE_METHOD, return_value=False):
        fallback_graph = pg.Gamma_Graph(points, gamma0=0.25, gamma1=0.5, closed=False)

    assert calls["fast"] == 0
    assert calls["fallback"] == 1
    assert _edge_list(graph) == _edge_list(fallback_graph)
