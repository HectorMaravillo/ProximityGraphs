"""Mathematical and structural invariants for public graph constructors."""

from dataclasses import dataclass

import numpy as np
import pytest

import proximitygraphs as pg

TRIANGLE = np.array(
    [
        [0.0, 0.0],
        [1.0, 0.0],
        [0.0, 1.0],
    ]
)

GENERAL_POSITION = np.array(
    [
        [0.0, 0.0],
        [1.0, 0.2],
        [0.4, 1.1],
        [1.6, 1.4],
        [2.2, 0.1],
        [2.8, 0.9],
    ]
)

GABRIEL_NON_EDGE = np.array(
    [
        [0.0, 0.0],
        [2.0, 0.0],
        [1.0, 0.1],
    ]
)

TOL = 1e-9


@dataclass(frozen=True)
class GraphSpec:
    name: str
    constructor: object
    kwargs: dict


GRAPH_SPECS = [
    GraphSpec("Complete", pg.GeometricGraph.complete, {}),
    GraphSpec("Unit_Disk", pg.Unit_Disk, {"dist_max": 1.25}),
    GraphSpec("DelaunayG", pg.DelaunayG, {}),
    GraphSpec("GG", pg.GG, {}),
    GraphSpec("RNG", pg.RNG, {}),
    GraphSpec("MST", pg.MST, {}),
    GraphSpec("NNG", pg.NNG, {"k": 2}),
    GraphSpec("SIG", pg.SIG, {}),
    GraphSpec("Sigma_Graph", pg.Sigma_Graph, {"sigma": 1.5}),
    GraphSpec("Beta_Skeleton", pg.Beta_Skeleton, {"beta": 1.5}),
    GraphSpec("Elliptic_GabrielG", pg.Elliptic_GabrielG, {"alpha": 1.5}),
    GraphSpec(
        "Gamma_Graph",
        pg.Gamma_Graph,
        {"gamma0": 0.0, "gamma1": 0.5, "block_size": 4},
    ),
    GraphSpec("Stepping_Stone", pg.Stepping_Stone, {"d": 2, "k": 0}),
    GraphSpec("Convex_Hull", pg.Convex_Hull, {}),
    GraphSpec("Alpha_Shape", pg.Alpha_Shape, {"alpha": 0.0}),
    GraphSpec("Alpha_Hull", pg.Alpha_Hull, {"alpha": 0.0, "n_points_per_arc": 5}),
    GraphSpec(
        "PhysarumGraph",
        pg.PhysarumGraph,
        {"steps": 2, "base_graph": "complete"},
    ),
    GraphSpec(
        "FungalGraph",
        pg.FungalGraph,
        {
            "steps": 2,
            "growth_iterations": 2,
            "prune_weak_factor": 0.0,
            "seed": 7,
        },
    ),
]

EXPERIMENT_SPECS = [spec for spec in GRAPH_SPECS if spec.name != "Complete"]

EUCLIDEAN_COVARIANT_SPECS = [
    spec
    for spec in GRAPH_SPECS
    if spec.name
    in {
        "Unit_Disk",
        "DelaunayG",
        "GG",
        "RNG",
        "MST",
        "NNG",
        "SIG",
        "Sigma_Graph",
        "Beta_Skeleton",
        "Elliptic_GabrielG",
        "Gamma_Graph",
        "Stepping_Stone",
        "Convex_Hull",
        "Alpha_Shape",
        "Alpha_Hull",
    }
]


def as_points(raw_points):
    return pg.SetPoints(np.asarray(raw_points, dtype=float))


def build_graph(spec, raw_points=GENERAL_POSITION):
    points = as_points(raw_points)
    return spec.constructor(points, **spec.kwargs)


def edge_set(graph):
    return {tuple(sorted(map(int, edge))) for edge in graph.graph.get_edgelist()}


def number_of_vertices(graph):
    return int(graph.graph.vcount())


def number_of_edges(graph):
    return int(graph.graph.ecount())


def has_edge(graph, i, j):
    return tuple(sorted((i, j))) in edge_set(graph)


def pairwise_distance(points, i, j):
    return float(np.linalg.norm(points[i] - points[j]))


def assert_valid_graph(graph, n, allow_self_loops=False):
    assert graph.n == n
    assert number_of_vertices(graph) == n
    assert graph.m == number_of_edges(graph)
    assert graph.m >= 0
    assert np.isfinite(graph.lengths).all()
    assert len(graph.lengths) == graph.m

    edges = graph.graph.get_edgelist()
    normalized = []
    for u, v in edges:
        assert isinstance(u, int)
        assert isinstance(v, int)
        assert 0 <= u < n
        assert 0 <= v < n
        if not allow_self_loops:
            assert u != v
        normalized.append(tuple(sorted((u, v))))

    assert len(normalized) == len(set(normalized))


@pytest.mark.parametrize("spec", GRAPH_SPECS, ids=lambda spec: spec.name)
def test_public_graph_constructors_have_valid_structure(spec):
    graph = build_graph(spec)

    assert_valid_graph(graph, len(GENERAL_POSITION))
    assert isinstance(graph.name, str)
    assert graph.graph.is_directed() is False


def test_graph_registry_tracks_public_graph_exports():
    expected_public_graphs = {
        "Alpha_Hull",
        "Alpha_Shape",
        "Beta_Skeleton",
        "Convex_Hull",
        "DelaunayG",
        "Elliptic_GabrielG",
        "FungalGraph",
        "GG",
        "Gamma_Graph",
        "MST",
        "NNG",
        "PhysarumGraph",
        "RNG",
        "SIG",
        "Sigma_Graph",
        "Stepping_Stone",
        "Unit_Disk",
    }
    registered = {spec.name for spec in GRAPH_SPECS}

    assert expected_public_graphs <= registered


def test_complete_graph_has_all_undirected_edges():
    graph = pg.GeometricGraph.complete(as_points(GENERAL_POSITION))
    n = len(GENERAL_POSITION)

    assert_valid_graph(graph, n)
    assert graph.m == n * (n - 1) // 2


def test_random_graph_boundary_probabilities():
    points = as_points(GENERAL_POSITION)
    empty = pg.GeometricGraph.random_graph(points, p=0.0)
    complete = pg.GeometricGraph.random_graph(points, p=1.0)
    n = len(GENERAL_POSITION)

    assert_valid_graph(empty, n)
    assert_valid_graph(complete, n)
    assert empty.m == 0
    assert complete.m == n * (n - 1) // 2


def test_mst_is_connected_acyclic_and_nonnegative():
    graph = pg.MST(as_points(GENERAL_POSITION))

    assert_valid_graph(graph, len(GENERAL_POSITION))
    assert graph.m == len(GENERAL_POSITION) - 1
    assert graph.graph.is_connected()
    assert graph.graph.is_tree()
    assert np.all(graph.lengths >= 0.0)


def test_unit_disk_edges_match_radius_threshold():
    radius = 1.1
    graph = pg.Unit_Disk(as_points(GENERAL_POSITION), dist_max=radius)

    assert_valid_graph(graph, len(GENERAL_POSITION))
    for i in range(len(GENERAL_POSITION)):
        for j in range(i + 1, len(GENERAL_POSITION)):
            expected = pairwise_distance(GENERAL_POSITION, i, j) <= radius + TOL
            assert has_edge(graph, i, j) is expected


def test_rng_gabriel_delaunay_inclusion_chain():
    rng_edges = edge_set(pg.RNG(as_points(GENERAL_POSITION)))
    gabriel_edges = edge_set(pg.GG(as_points(GENERAL_POSITION)))
    delaunay_edges = edge_set(pg.DelaunayG(as_points(GENERAL_POSITION)))

    assert rng_edges <= gabriel_edges
    assert gabriel_edges <= delaunay_edges


def test_gabriel_empty_diameter_disk_invariant_and_non_edge():
    graph = pg.GG(as_points(GENERAL_POSITION))

    for i, j in edge_set(graph):
        center = 0.5 * (GENERAL_POSITION[i] + GENERAL_POSITION[j])
        radius_sq = 0.25 * np.sum((GENERAL_POSITION[i] - GENERAL_POSITION[j]) ** 2)
        for k in set(range(len(GENERAL_POSITION))) - {i, j}:
            dist_sq = np.sum((GENERAL_POSITION[k] - center) ** 2)
            assert dist_sq >= radius_sq - TOL

    non_edge_graph = pg.GG(as_points(GABRIEL_NON_EDGE))
    assert not has_edge(non_edge_graph, 0, 1)


def test_relative_neighborhood_lune_invariant_and_non_edge():
    graph = pg.RNG(as_points(GENERAL_POSITION))

    for i, j in edge_set(graph):
        dij = pairwise_distance(GENERAL_POSITION, i, j)
        for k in set(range(len(GENERAL_POSITION))) - {i, j}:
            dik = pairwise_distance(GENERAL_POSITION, i, k)
            djk = pairwise_distance(GENERAL_POSITION, j, k)
            assert max(dik, djk) >= dij - TOL

    non_edge_graph = pg.RNG(as_points(GABRIEL_NON_EDGE))
    assert not has_edge(non_edge_graph, 0, 1)


@pytest.mark.parametrize("spec", EUCLIDEAN_COVARIANT_SPECS, ids=lambda spec: spec.name)
def test_euclidean_graphs_are_translation_rotation_and_scale_covariant(spec):
    base = edge_set(build_graph(spec))

    theta = np.pi / 7
    rotation = np.array(
        [
            [np.cos(theta), -np.sin(theta)],
            [np.sin(theta), np.cos(theta)],
        ]
    )
    transformed_sets = [
        GENERAL_POSITION + np.array([10.0, -3.0]),
        GENERAL_POSITION @ rotation.T,
    ]
    if spec.name != "Unit_Disk":
        transformed_sets.append(3.5 * GENERAL_POSITION)

    for transformed in transformed_sets:
        assert edge_set(build_graph(spec, transformed)) == base


@pytest.mark.parametrize("spec", GRAPH_SPECS[-2:], ids=lambda spec: spec.name)
def test_bio_inspired_graphs_are_deterministic_with_fixed_configuration(spec):
    first = build_graph(spec)
    second = build_graph(spec)

    assert_valid_graph(first, len(GENERAL_POSITION))
    assert edge_set(first) == edge_set(second)


def test_experiment_builds_requested_graph_families_and_stores_graphs():
    exp = pg.Experiment(
        name="invariant-smoke",
        point_config={"method": "uniform_square", "params": {"n": 6}},
        graph_configs=[
            {"class": spec.constructor, "params": spec.kwargs, "name": spec.name}
            for spec in EXPERIMENT_SPECS
        ],
        n_simulations=1,
        seed=42,
        verbose=False,
    )
    exp.add_custom_metric("edge_count_again", lambda graph: graph.m)

    results = exp.run(store_graphs=True)
    graph_names = {spec.name for spec in EXPERIMENT_SPECS}

    assert set(results["graph_type"]) == graph_names
    assert set(results["n_vertices"]) == {6}
    assert set(results["edge_count_again"]) == set(results["n_edges"])
    assert {entry["graph_type"] for entry in exp._raw_graphs} == graph_names
    for entry in exp._raw_graphs:
        assert_valid_graph(entry["graph"], 6)


def test_experiment_results_are_deterministic_for_fixed_seed():
    def run_once():
        exp = pg.Experiment(
            name="deterministic",
            point_config={"method": "uniform_square", "params": {"n": 6}},
            graph_configs=[
                {"class": pg.GG, "params": {}, "name": "GG"},
                {"class": pg.RNG, "params": {}, "name": "RNG"},
            ],
            n_simulations=2,
            seed=123,
            verbose=False,
        )
        return (
            exp.run().sort_values(["simulation", "graph_type"]).reset_index(drop=True)
        )

    first = run_once()
    second = run_once()

    assert first.equals(second)
