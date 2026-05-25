"""Installed-package smoke test for release validation."""

import numpy as np

import proximitygraphs as pg


def assert_graph_invariants(graph, points):
    assert graph.n == points.n
    assert graph.m >= 0
    assert graph.graph.vcount() == points.n
    assert graph.graph.ecount() == graph.m


def main():
    print(f"proximitygraphs {pg.__version__}")

    points = pg.SetPoints(np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]]))
    graph_specs = [
        (pg.MST, {}),
        (pg.Unit_Disk, {"dist_max": 1.01}),
        (pg.GG, {}),
        (pg.RNG, {}),
        (pg.DelaunayG, {}),
    ]

    if hasattr(pg, "Gamma_Graph"):
        graph_specs.append((pg.Gamma_Graph, {"gamma0": -1.0, "gamma1": -1.0}))

    for graph_class, kwargs in graph_specs:
        graph = graph_class(points, **kwargs)
        assert_graph_invariants(graph, points)
        print(f"{graph_class.__name__}: n={graph.n}, m={graph.m}")


if __name__ == "__main__":
    main()
