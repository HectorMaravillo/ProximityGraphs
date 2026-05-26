import numpy as np

from proximitygraphs.points import SetPoints


def _points():
    return SetPoints(
        np.array(
            [
                [0.0, 0.0],
                [1.0, 0.0],
                [0.0, 1.0],
                [1.0, 1.0],
            ]
        )
    )


def test_import_from_biological_package():
    from proximitygraphs.biological import BiologicalGraph, FungalGraph, PhysarumGraph

    assert BiologicalGraph.__name__ == "BiologicalGraph"
    assert PhysarumGraph.__name__ == "PhysarumGraph"
    assert FungalGraph.__name__ == "FungalGraph"


def test_import_from_biologicalgraphs_wrapper():
    from proximitygraphs.biological import (
        BiologicalGraph,
        FungalGraph,
        PhysarumGraph,
    )
    from proximitygraphs.biologicalgraphs import (
        BiologicalGraph as WrappedBiologicalGraph,
    )
    from proximitygraphs.biologicalgraphs import (
        FungalGraph as WrappedFungalGraph,
    )
    from proximitygraphs.biologicalgraphs import (
        PhysarumGraph as WrappedPhysarumGraph,
    )

    assert WrappedBiologicalGraph is BiologicalGraph
    assert WrappedPhysarumGraph is PhysarumGraph
    assert WrappedFungalGraph is FungalGraph


def test_construct_physarum_graph():
    from proximitygraphs.biological import PhysarumGraph

    points = _points()
    graph = PhysarumGraph(points, steps=0)

    assert graph.name == "Physarum Graph"
    assert graph.n == points.n
    assert graph.graph.vcount() == points.n


def test_construct_fungal_graph():
    from proximitygraphs.biological import FungalGraph

    points = _points()
    graph = FungalGraph(
        points,
        growth_iterations=0,
        prune_weak_factor=0,
        steps=0,
        seed=42,
    )

    assert graph.name == "Fungal Graph"
    assert graph.n == points.n
    assert graph.graph.vcount() == points.n
