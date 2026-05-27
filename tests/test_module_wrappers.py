import numpy as np


def test_point_package_and_points_wrapper_export_same_class():
    from proximitygraphs.point import SetPoints
    from proximitygraphs.point.generators.uniform_square import uniform_square
    from proximitygraphs.point.transformations.rotation import rotation
    from proximitygraphs.points import SetPoints as WrappedSetPoints

    assert WrappedSetPoints is SetPoints
    assert SetPoints(np.array([[0.0, 0.0], [1.0, 0.0]])).n == 2
    assert SetPoints.uniform_square.__func__ is uniform_square
    assert SetPoints.rotation is rotation


def test_geometric_package_and_geometricgraphs_wrapper_export_same_names():
    from proximitygraphs.geometric import GeometricGraph, draw_grid, load_graph
    from proximitygraphs.geometricgraphs import (
        GeometricGraph as WrappedGeometricGraph,
    )
    from proximitygraphs.geometricgraphs import (
        draw_grid as wrapped_draw_grid,
    )
    from proximitygraphs.geometricgraphs import (
        load_graph as wrapped_load_graph,
    )

    assert WrappedGeometricGraph is GeometricGraph
    assert wrapped_draw_grid is draw_grid
    assert wrapped_load_graph is load_graph


def test_envelope_package_and_envelops_wrapper_export_same_functions():
    from proximitygraphs.envelope import smallest_circle
    from proximitygraphs.envelops import smallest_circle as wrapped_smallest_circle

    points = np.array([[0.0, 0.0], [2.0, 0.0]])
    center, radius = smallest_circle(points)

    assert wrapped_smallest_circle is smallest_circle
    assert np.allclose(center, [1.0, 0.0])
    assert radius == 1.0


def test_experiment_package_and_experiments_wrapper_export_same_class():
    from proximitygraphs.experiment import Experiment
    from proximitygraphs.experiments import Experiment as WrappedExperiment

    assert WrappedExperiment is Experiment


def test_utilities_package_and_utils_wrapper_export_same_function():
    from proximitygraphs.utilities import points_on_sphere
    from proximitygraphs.utils import points_on_sphere as wrapped_points_on_sphere

    assert wrapped_points_on_sphere is points_on_sphere
    assert points_on_sphere(3, seed=0).shape == (3, 2)
