"""Edge cases and validation behavior for small deterministic inputs."""

import numpy as np
import pytest
from scipy.spatial import QhullError

import proximitygraphs as pg


def _edges(graph):
    return sorted(graph.graph.get_edgelist())


@pytest.mark.parametrize(
    "factory",
    [
        lambda: pg.SetPoints.uniform_square(n=0),
        lambda: pg.SetPoints.uniform_sphere(n=0),
        lambda: pg.SetPoints.uniform_over_sphere(n=0),
        lambda: pg.SetPoints.normal_dist(n=0),
        lambda: pg.SetPoints.grid(shape=(0, 2)),
        lambda: pg.SetPoints.grid(shape=(2,)),
    ],
)
def test_invalid_point_constructors_raise_meaningful_errors(factory):
    with pytest.raises(ValueError):
        factory()


def test_setpoints_requires_numpy_array():
    with pytest.raises(TypeError, match="numpy.ndarray"):
        pg.SetPoints([[0.0, 0.0], [1.0, 0.0]])


def test_unit_disk_rejects_invalid_parameters():
    points = pg.SetPoints.grid(shape=(2, 2))

    with pytest.raises(TypeError, match="dist_max"):
        pg.Unit_Disk(points, dist_max="1")
    with pytest.raises(ValueError, match="non-negative"):
        pg.Unit_Disk(points, dist_max=-1.0)
    with pytest.raises(TypeError, match="closed"):
        pg.Unit_Disk(points, dist_max=1.0, closed="yes")


def test_beta_and_gamma_reject_invalid_parameters():
    points = pg.SetPoints.grid(shape=(2, 2))

    with pytest.raises(ValueError):
        pg.Beta_Skeleton(points, beta=0)
    with pytest.raises(TypeError, match="closed"):
        pg.Gamma_Graph(points, closed="yes")


def test_delaunay_based_graphs_raise_qhull_error_for_too_few_points():
    points = pg.SetPoints(np.array([[0.0, 0.0], [1.0, 0.0]]))

    for graph_class in [pg.DelaunayG, pg.MST, pg.GG, pg.RNG]:
        with pytest.raises(QhullError):
            graph_class(points)


def test_collinear_points_raise_qhull_error_for_delaunay_based_graphs():
    points = pg.SetPoints(np.array([[0.0, 0.0], [1.0, 0.0], [2.0, 0.0]]))

    for graph_class in [pg.DelaunayG, pg.MST, pg.GG, pg.RNG]:
        with pytest.raises(QhullError):
            graph_class(points)


def test_duplicate_points_are_supported_by_distance_based_graphs():
    points = pg.SetPoints(np.array([[0.0, 0.0], [0.0, 0.0], [1.0, 0.0]]))

    unit_disk = pg.Unit_Disk(points, dist_max=1.0)
    gamma = pg.Gamma_Graph(points, gamma0=-1.0, gamma1=-1.0)

    assert unit_disk.n == points.n
    assert gamma.n == points.n
    assert _edges(unit_disk) == [(0, 1), (0, 2), (1, 2)]
    assert _edges(gamma) == [(0, 1), (0, 2), (1, 2)]


def test_plotting_uses_noninteractive_backend_without_opening_windows():
    points = pg.SetPoints.grid(shape=(2, 2))
    graph = pg.Unit_Disk(points, dist_max=1.01)

    fig, ax = graph.draw(title=False)
    try:
        assert fig is ax.figure
        assert len(ax.collections) >= 1
    finally:
        import matplotlib.pyplot as plt

        plt.close(fig)
