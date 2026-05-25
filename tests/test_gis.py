"""Optional GIS export tests."""

import pytest

geopandas = pytest.importorskip("geopandas")
pytest.importorskip("shapely")

import proximitygraphs as pg


pytestmark = pytest.mark.gis


def test_to_gpd_lines_returns_geodataframe_with_one_row_per_edge():
    points = pg.SetPoints.grid(shape=(2, 2))
    graph = pg.Unit_Disk(points, dist_max=1.01)

    lines = graph.to_gpd_lines()

    assert isinstance(lines, geopandas.GeoDataFrame)
    assert len(lines) == graph.m
    assert lines.geometry.name == "geometry"
    assert lines.geometry.geom_type.tolist() == ["LineString"] * graph.m
    assert {"union_initial", "union_final", "dist_eucl", "geometry"} <= set(lines)
    assert lines.crs is None


def test_to_gpd_lines_handles_empty_graph():
    points = pg.SetPoints.grid(shape=(2, 2))
    graph = pg.Unit_Disk(points, dist_max=0.5)

    lines = graph.to_gpd_lines()

    assert isinstance(lines, geopandas.GeoDataFrame)
    assert lines.empty
    assert list(lines.columns) == ["union_initial", "union_final", "geometry"]


def test_to_gpd_polygons_polygonizes_small_cycle():
    points = pg.SetPoints.grid(shape=(2, 2))
    graph = pg.Unit_Disk(points, dist_max=1.01)

    polygons = graph.to_gpd_polygons()

    assert isinstance(polygons, geopandas.GeoDataFrame)
    assert len(polygons) == 1
    assert polygons.geometry.iloc[0].geom_type == "Polygon"
