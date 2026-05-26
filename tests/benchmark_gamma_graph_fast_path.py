"""Small benchmark for the conservative Gamma_Graph planar fast path."""

from time import perf_counter
from unittest.mock import patch

import proximitygraphs as pg

CAN_USE_METHOD = "_Gamma_Graph__can_use_planar_fast_gamma"


def timed_build(points, use_fast, repeats=3):
    timings = []
    graph = None

    for _ in range(repeats):
        start = perf_counter()
        if use_fast:
            graph = pg.Gamma_Graph(points, gamma0=0.25, gamma1=0.75, closed=False)
        else:
            with patch.object(pg.Gamma_Graph, CAN_USE_METHOD, return_value=False):
                graph = pg.Gamma_Graph(points, gamma0=0.25, gamma1=0.75, closed=False)
        timings.append(perf_counter() - start)

    return graph, min(timings)


def main():
    # The current fallback is heavily vectorized, so the crossover appears on
    # larger but still practical planar inputs.
    points = pg.SetPoints.uniform_square(n=4000, seed=20260330)

    fast_graph, fast_time = timed_build(points, use_fast=True)
    fallback_graph, fallback_time = timed_build(points, use_fast=False)

    if sorted(fast_graph.graph.get_edgelist()) != sorted(
        fallback_graph.graph.get_edgelist()
    ):
        raise AssertionError("Fast path does not match the preserved fallback graph.")

    speedup = fallback_time / fast_time if fast_time > 0.0 else float("inf")

    print(f"points: {points.n}")
    print(f"fast path: {fast_time:.6f}s")
    print(f"fallback: {fallback_time:.6f}s")
    print(f"speedup: {speedup:.2f}x")


if __name__ == "__main__":
    main()
