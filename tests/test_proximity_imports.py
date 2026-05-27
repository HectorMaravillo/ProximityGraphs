import numpy as np

from proximitygraphs.points import SetPoints

PUBLIC_CLASSES = [
    "Alpha_Hull",
    "Alpha_Shape",
    "Beta_Skeleton",
    "Convex_Hull",
    "DelaunayG",
    "Elliptic_GabrielG",
    "GG",
    "Gamma_Graph",
    "MST",
    "NNG",
    "ProximityGraph",
    "RNG",
    "SIG",
    "Sigma_Graph",
    "Stepping_Stone",
    "Unit_Disk",
]


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


def test_import_from_proximity_package():
    import proximitygraphs.proximity as proximity

    for class_name in PUBLIC_CLASSES:
        assert getattr(proximity, class_name).__name__ == class_name


def test_import_from_proximitygraphs_wrapper():
    import proximitygraphs.proximity as proximity
    import proximitygraphs.proximitygraphs as wrapper

    for class_name in PUBLIC_CLASSES:
        assert getattr(wrapper, class_name) is getattr(proximity, class_name)


def test_beta_special_cases_import_from_new_modules_and_beta_wrapper():
    from proximitygraphs.proximity.beta import GG as WrappedGG
    from proximitygraphs.proximity.beta import RNG as WrappedRNG
    from proximitygraphs.proximity.gabriel import GG
    from proximitygraphs.proximity.relateve import RNG

    assert WrappedGG is GG
    assert WrappedRNG is RNG


def test_construct_unit_disk_graph():
    from proximitygraphs.proximity import Unit_Disk

    points = _points()
    graph = Unit_Disk(points, dist_max=1.01)

    assert graph.name == "Unit Disk Graph"
    assert graph.n == points.n
    assert graph.graph.vcount() == points.n


def test_construct_gamma_graph():
    from proximitygraphs.proximity import Gamma_Graph

    points = _points()
    graph = Gamma_Graph(points, gamma0=-1.0, gamma1=-1.0)

    assert graph.name == "gamma-Neighborhood Graph"
    assert graph.n == points.n
    assert graph.graph.vcount() == points.n
