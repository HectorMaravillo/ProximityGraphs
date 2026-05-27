"""GIS conversion and persistence methods attached to ``GeometricGraph``."""

import numpy as np


def _require_gis_dependencies():
    try:
        from geopandas import GeoDataFrame, GeoSeries
    except ImportError as exc:
        raise ImportError(
            "GeoDataFrame export requires the optional GIS dependencies. "
            "Install them with: pip install -e .[gis]"
        ) from exc

    try:
        from shapely.geometry import LineString
        from shapely.ops import polygonize
    except ImportError as exc:
        raise ImportError(
            "Polygon and line export requires the optional GIS dependencies. "
            "Install them with: pip install -e .[gis]"
        ) from exc

    return GeoDataFrame, GeoSeries, LineString, polygonize


def save(self, path, filename):
    """
    Save the GeometricGraph to disk given a path and filename (without extension).
    Saves a .npy file for the points and a .pickle file for the graph structure.
    Parameters
    ----------
    path : str
        The directory path where the files are stored.
    filename : str
        The base filename (without extension) for the graph files.
    """
    self._GeometricGraph__graph["name"] = self.name
    self._GeometricGraph__graph["details"] = self.details
    if not path.endswith(("/", "\\")):
        path += "/"
    self._GeometricGraph__graph.write_pickle(path + filename)
    np.save(path + filename + ".npy", self.points)
    del self._GeometricGraph__graph["name"]
    del self._GeometricGraph__graph["details"]


def to_gpd_lines(self):
    """Convert the edges of the graph to a GeoDataFrame of LineStrings."""
    GeoDataFrame, GeoSeries, LineString, _ = _require_gis_dependencies()

    if self.m == 0:
        return GeoDataFrame(columns=["union_initial", "union_final", "geometry"])

    if self.m > 0:
        _ = self.lengths
        _ = self.orientation

    point_coords = self.points

    if self.setpoints.dim != 2:
        raise ValueError(
            "Points must be a 2D array with shape (n, dim) where n"
            "is the number of points and dim is the dimension."
        )

    lines_geom = []
    edges = self.graph.get_edgelist()
    for u, v in edges:
        p1 = point_coords[u]
        p2 = point_coords[v]
        lines_geom.append(LineString([p1, p2]))
    gpd_lines = GeoDataFrame(geometry=GeoSeries(lines_geom))
    attr_names = self.graph.es.attribute_names()
    for attr_name in attr_names:
        gpd_lines[attr_name] = self.graph.es[attr_name]
    gpd_lines["union_initial"] = np.array(edges)[:, 0]
    gpd_lines["union_final"] = np.array(edges)[:, 1]
    final_columns = (
        ["union_initial", "union_final"]
        + [name for name in attr_names if name not in ["union_initial", "union_final"]]
        + ["geometry"]
    )
    final_columns = [col for col in final_columns if col in gpd_lines.columns]
    return gpd_lines[final_columns]


def to_gpd_polygons(self):
    """Convert the internal faces of the graph to a GeoDataFrame of polygons."""
    GeoDataFrame, _, _, polygonize = _require_gis_dependencies()

    if self.setpoints.dim != 2:
        raise ValueError("Points must be a 2D array with shape (n, dim) ")
    if (self.cc - self.n + self.m) <= 0:
        raise TypeError(
            "The graph has no internal faces to polygonize "
            "(e.g., it's a tree or a line)."
        )
    gpd_lines = self.to_gpd_lines()
    if gpd_lines.empty:
        raise ValueError("Cannot create polygons from a graph with no edges.")
    polygons = list(polygonize(gpd_lines["geometry"]))
    if not polygons:
        raise ValueError(
            "Polygonization did not result in any polygons."
            "Ensure the graph forms closed regions."
        )
    return GeoDataFrame(geometry=polygons)
