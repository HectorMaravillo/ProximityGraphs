"""Runs a seeded regression suite for proximity graphs against a saved snapshot."""

import json
from pathlib import Path

import numpy as np
import pytest

import proximitygraphs as pg

SNAPSHOT_PATH = Path(__file__).parent / "data" / "proximity_graph_regression.json"
EXPECTED_SNAPSHOT = json.loads(SNAPSHOT_PATH.read_text())

POINT_CONFIG = {
    "method": "uniform_square",
    "params": {"n": 12, "seed": 20260328},
}

GRAPH_SPECS = [
    {"class": pg.DelaunayG, "name": "delaunay", "params": {}},
    {"class": pg.Convex_Hull, "name": "convex_hull", "params": {}},
    {"class": pg.MST, "name": "mst", "params": {}},
    {
        "class": pg.Beta_Skeleton,
        "name": "beta_skeleton_circle",
        "params": {"beta": 1.5, "type_region": "circle", "closed": False},
    },
    {
        "class": pg.Beta_Skeleton,
        "name": "beta_skeleton_lune",
        "params": {"beta": 1.5, "type_region": "lune", "closed": False},
    },
    {
        "class": pg.Beta_Skeleton,
        "name": "beta_skeleton_intersection",
        "params": {"beta": 0.75, "type_region": "intersection", "closed": False},
    },
    {"class": pg.RNG, "name": "rng", "params": {"closed": False}},
    {"class": pg.GG, "name": "gg", "params": {"closed": True}},
    {
        "class": pg.Stepping_Stone,
        "name": "stepping_stone",
        "params": {"d": 1.5, "k": 0, "closed": False},
    },
    {
        "class": pg.Stepping_Stone,
        "name": "stepping_stone_d2_k1",
        "params": {"d": 2.0, "k": 1, "closed": False},
    },
    {"class": pg.NNG, "name": "nng", "params": {"k": 1}},
    {"class": pg.NNG, "name": "nng_k2", "params": {"k": 2}},
    {
        "class": pg.Sigma_Graph,
        "name": "sigma_graph",
        "params": {"sigma": 2.0, "closed": False},
    },
    {
        "class": pg.Unit_Disk,
        "name": "unit_disk",
        "params": {"dist_max": 0.35, "closed": True},
    },
    {"class": pg.SIG, "name": "sig", "params": {"closed": False}},
    {
        "class": pg.Elliptic_GabrielG,
        "name": "elliptic_gabriel",
        "params": {"alpha": 1.5, "closed": False},
    },
    {"class": pg.Alpha_Shape, "name": "alpha_shape", "params": {"alpha": -1.5}},
    {"class": pg.Alpha_Shape, "name": "alpha_shape_convex", "params": {"alpha": 0.0}},
    {
        "class": pg.Alpha_Hull,
        "name": "alpha_hull",
        "params": {"alpha": -1.5, "n_points_per_arc": 20},
    },
    {
        "class": pg.Alpha_Hull,
        "name": "alpha_hull_convex",
        "params": {"alpha": 0.0, "n_points_per_arc": 20},
    },
    {
        "class": pg.Gamma_Graph,
        "name": "gamma_graph",
        "params": {"gamma0": 0.25, "gamma1": 0.75, "closed": False, "block_size": 16},
    },
    {
        "class": pg.Gamma_Graph,
        "name": "gamma_graph_complete",
        "params": {"gamma0": -1.0, "gamma1": -1.0, "closed": False},
    },
    {
        "class": pg.Gamma_Graph,
        "name": "gamma_graph_void",
        "params": {"gamma0": 1.0, "gamma1": 1.0, "closed": False},
    },
    {
        "class": pg.Gamma_Graph,
        "name": "gamma_graph_convex_hull",
        "params": {"gamma0": -1.0, "gamma1": 1.0, "closed": False},
    },
    {
        "class": pg.PhysarumGraph,
        "name": "physarum_complete_base",
        "params": {"steps": 2, "base_graph": "complete"},
    },
    {
        "class": pg.FungalGraph,
        "name": "fungal_seeded",
        "params": {
            "steps": 2,
            "growth_iterations": 2,
            "prune_weak_factor": 0.0,
            "seed": 20260328,
        },
    },
]

FLOAT_METRICS = [
    "mean_degree",
    "std_degree",
    "min_degree",
    "max_degree",
    "mean_length",
    "std_length",
    "min_length",
    "max_length",
    "total_length",
    "entropy_degree",
    "entropy_length",
    "entropy_orientation",
    "density",
]

INT_METRICS = [
    "simulation",
    "n_vertices",
    "n_edges",
    "n_components",
    "n_faces",
]


def build_current_snapshot():
    experiment = pg.Experiment(
        name="Seeded Proximity Graph Regression",
        point_config=POINT_CONFIG,
        graph_configs=GRAPH_SPECS,
        n_simulations=1,
        verbose=False,
    )
    results = experiment.run(store_graphs=True)

    first_graph_name = GRAPH_SPECS[0]["name"]
    first_graph = experiment.get_graph(0, first_graph_name)
    assert first_graph is not None

    snapshot = {
        "point_config": POINT_CONFIG,
        "graph_order": [spec["name"] for spec in GRAPH_SPECS],
        "points": np.round(first_graph.points, 12).tolist(),
        "graphs": {},
    }

    for _, row in results.sort_values("graph_type").iterrows():
        graph_name = row["graph_type"]
        graph = experiment.get_graph(int(row["simulation"]), graph_name)
        assert graph is not None

        metrics = {"graph_type": graph_name}
        for metric in INT_METRICS:
            metrics[metric] = int(row[metric])
        for metric in FLOAT_METRICS:
            metrics[metric] = round(float(row[metric]), 12)
        metrics["is_connected"] = bool(row["is_connected"])

        snapshot["graphs"][graph_name] = {
            "metrics": metrics,
            "edges": [list(edge) for edge in sorted(graph.graph.get_edgelist())],
        }

    return snapshot


@pytest.fixture(scope="module")
def current_snapshot():
    return build_current_snapshot()


def test_seeded_experiment_matches_saved_points(current_snapshot):
    assert current_snapshot["point_config"] == EXPECTED_SNAPSHOT["point_config"]
    assert current_snapshot["graph_order"] == EXPECTED_SNAPSHOT["graph_order"]
    assert np.allclose(current_snapshot["points"], EXPECTED_SNAPSHOT["points"])


def test_seeded_experiment_covers_all_saved_graphs(current_snapshot):
    assert set(current_snapshot["graphs"]) == set(EXPECTED_SNAPSHOT["graphs"])


@pytest.mark.parametrize("graph_name", EXPECTED_SNAPSHOT["graph_order"])
def test_proximity_graph_snapshot_metrics_and_edges(graph_name, current_snapshot):
    actual = current_snapshot["graphs"][graph_name]
    expected = EXPECTED_SNAPSHOT["graphs"][graph_name]

    assert actual["edges"] == expected["edges"]
    assert actual["metrics"]["graph_type"] == expected["metrics"]["graph_type"]
    assert actual["metrics"]["is_connected"] == expected["metrics"]["is_connected"]

    for metric in INT_METRICS:
        assert actual["metrics"][metric] == expected["metrics"][metric]

    for metric in FLOAT_METRICS:
        assert actual["metrics"][metric] == pytest.approx(
            expected["metrics"][metric],
            rel=1e-9,
            abs=1e-9,
        )
