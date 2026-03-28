"""Covers small smoke tests for examples and a few stable graph behaviors."""

import importlib.util
from pathlib import Path

import numpy as np

import proximitygraphs as pg


def load_quickstart_module():
    quickstart_path = Path(__file__).resolve().parents[1] / "examples" / "quickstart.py"
    spec = importlib.util.spec_from_file_location("quickstart", quickstart_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_uniform_square_is_reproducible_with_seed():
    points_a = pg.SetPoints.uniform_square(n=5, seed=123)
    points_b = pg.SetPoints.uniform_square(n=5, seed=123)

    assert points_a.n == 5
    assert points_a.dim == 2
    assert np.allclose(points_a.points, points_b.points)


def test_mst_on_2x2_grid_has_tree_structure_and_unit_lengths():
    points = pg.SetPoints.grid(shape=(2, 2))
    graph = pg.MST(points)

    assert graph.n == 4
    assert graph.m == graph.n - 1
    assert graph.graph.is_tree()
    assert np.allclose(np.sort(graph.lengths), np.ones(3))


def test_gamma_graph_special_cases_match_documented_extremes():
    points = pg.SetPoints.grid(shape=(2, 2))

    void_graph = pg.Gamma_Graph(points, gamma0=1.0, gamma1=1.0)
    complete_graph = pg.Gamma_Graph(points, gamma0=-1.0, gamma1=-1.0)

    assert void_graph.m == 0
    assert complete_graph.m == 6
    assert sorted(complete_graph.graph.get_edgelist()) == [
        (0, 1),
        (0, 2),
        (0, 3),
        (1, 2),
        (1, 3),
        (2, 3),
    ]


def test_quickstart_main_prints_expected_summary(capsys):
    quickstart = load_quickstart_module()

    quickstart.main()
    captured = capsys.readouterr()

    assert captured.out.splitlines() == [
        "points: 9",
        "mst edges: 8",
        "unit disk edges: 12",
        "unit disk edge list: [(0, 1), (0, 3), (1, 2), (1, 4), (2, 5), (3, 4), (3, 6), (4, 5), (4, 7), (5, 8), (6, 7), (7, 8)]",
    ]
