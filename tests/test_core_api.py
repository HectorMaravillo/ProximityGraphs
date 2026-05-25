"""Deterministic coverage for the public core API."""

import sys
from subprocess import run

import numpy as np

import proximitygraphs as pg


def _edges(graph):
    return sorted(graph.graph.get_edgelist())


def _assert_graph_invariants(graph, points):
    assert graph.n == points.n
    assert graph.m >= 0
    assert graph.graph.vcount() == points.n
    assert graph.graph.ecount() == graph.m
    assert len(graph.lengths) == graph.m


def test_package_import_and_version_are_public():
    assert isinstance(pg.__version__, str)
    assert pg.__version__
    assert pg.SetPoints is not None
    assert pg.GeometricGraph is not None
    assert pg.Gamma_Graph is not None


def test_core_import_does_not_require_optional_gis_dependencies():
    code = """
import builtins

original_import = builtins.__import__

def guarded_import(name, *args, **kwargs):
    if name == "geopandas" or name.startswith("geopandas."):
        raise ImportError("geopandas intentionally unavailable")
    if name == "shapely" or name.startswith("shapely."):
        raise ImportError("shapely intentionally unavailable")
    return original_import(name, *args, **kwargs)

builtins.__import__ = guarded_import

import proximitygraphs as pg

assert pg.SetPoints.uniform_square(n=3, seed=1).n == 3
"""
    result = run([sys.executable, "-c", code], check=False, capture_output=True)

    assert result.returncode == 0, result.stderr.decode()


def test_point_set_constructors_have_expected_shapes_and_reproducibility():
    random_constructors = [
        pg.SetPoints.uniform_square,
        pg.SetPoints.uniform_sphere,
        pg.SetPoints.uniform_over_sphere,
        pg.SetPoints.normal_dist,
    ]
    for constructor in random_constructors:
        points_a = constructor(n=6, seed=123)
        points_b = constructor(n=6, seed=123)

        assert points_a.n == 6
        assert points_a.dim == 2
        assert points_a.points.shape == (6, 2)
        assert np.allclose(points_a.points, points_b.points)

    assert pg.SetPoints.grid(shape=(2, 2)).points.shape == (4, 2)
    assert pg.SetPoints.grid(shape=(3, 3)).points.shape == (9, 2)
    assert pg.SetPoints.hexagonal(n_x=1, n_y=1).dim == 2
    assert pg.SetPoints.triangular(n_x=1, n_y=1).dim == 2


def test_small_deterministic_graphs_have_stable_edges():
    triangle = pg.SetPoints(np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]]))

    expected_edges = {
        pg.Unit_Disk: [(0, 1), (0, 2)],
        pg.GG: [(0, 1), (0, 2)],
        pg.RNG: [(0, 1), (0, 2)],
        pg.DelaunayG: [(0, 1), (0, 2), (1, 2)],
        pg.MST: [(0, 1), (0, 2)],
    }

    for graph_class, edges in expected_edges.items():
        if graph_class is pg.Unit_Disk:
            graph = graph_class(triangle, dist_max=1.01)
        else:
            graph = graph_class(triangle)

        _assert_graph_invariants(graph, triangle)
        assert _edges(graph) == edges


def test_grid_graph_invariants_and_expected_counts():
    for points in [pg.SetPoints.grid(shape=(2, 2)), pg.SetPoints.grid(shape=(3, 3))]:
        graph_specs = [
            (pg.Unit_Disk, {"dist_max": 1.01}),
            (pg.GG, {}),
            (pg.RNG, {}),
            (pg.DelaunayG, {}),
            (pg.Gamma_Graph, {"gamma0": -1.0, "gamma1": -1.0}),
        ]
        for graph_class, kwargs in graph_specs:
            graph = graph_class(points, **kwargs)
            _assert_graph_invariants(graph, points)

        mst = pg.MST(points)
        _assert_graph_invariants(mst, points)
        assert mst.m == points.n - 1
        assert mst.graph.is_tree()


def test_repeated_graph_construction_is_deterministic():
    points = pg.SetPoints.grid(shape=(3, 3))

    graph_specs = [
        (pg.MST, {}),
        (pg.Unit_Disk, {"dist_max": 1.01}),
        (pg.GG, {}),
        (pg.RNG, {}),
        (pg.DelaunayG, {}),
        (pg.Gamma_Graph, {"gamma0": 0.25, "gamma1": 0.75, "block_size": 8}),
    ]

    for graph_class, kwargs in graph_specs:
        first = graph_class(points, **kwargs)
        second = graph_class(points, **kwargs)
        assert _edges(first) == _edges(second)


def test_unit_disk_and_gamma_two_point_cases():
    points = pg.SetPoints(np.array([[0.0, 0.0], [1.0, 0.0]]))

    unit_disk = pg.Unit_Disk(points, dist_max=1.0)
    gamma = pg.Gamma_Graph(points, gamma0=-1.0, gamma1=-1.0)

    assert _edges(unit_disk) == [(0, 1)]
    assert _edges(gamma) == [(0, 1)]
