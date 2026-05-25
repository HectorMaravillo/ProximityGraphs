"""Checks package imports and a few core API behaviors on tiny inputs."""

import numpy as np
import pytest

import proximitygraphs as pg


def test_import_smoke():
    assert pg.__version__ == "0.1.0a1"
    assert hasattr(pg, "SetPoints")
    assert hasattr(pg, "Unit_Disk")


def test_unit_disk_edges_on_grid():
    points = pg.SetPoints.grid(shape=(2, 2))
    graph = pg.Unit_Disk(points, dist_max=1.01)

    assert graph.n == 4
    assert graph.m == 4
    assert sorted(graph.graph.get_edgelist()) == [
        (0, 1),
        (0, 2),
        (1, 3),
        (2, 3),
    ]
    assert np.allclose(np.sort(graph.lengths), np.ones(4))


def test_uniform_square_rejects_invalid_n():
    with pytest.raises(ValueError, match="positive integer"):
        pg.SetPoints.uniform_square(n=0)
