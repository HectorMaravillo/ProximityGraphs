"""GIS conversion functions attached to ``SetPoints``."""

import numpy as np


def _require_gis_dependencies():
    try:
        import geopandas as gpd
    except ImportError as exc:
        raise ImportError(
            "GeoPandas support requires the optional GIS dependencies. "
            "Install them with: pip install -e .[gis]"
        ) from exc

    try:
        from shapely.geometry import Point
    except ImportError as exc:
        raise ImportError(
            "Shapely support requires the optional GIS dependencies. "
            "Install them with: pip install -e .[gis]"
        ) from exc

    return gpd, Point


def from_geopandas(cls, geoseries, seed=None):
    """
    Creates a SetPoints object from a geopandas.GeoSeries of Points.

    Parameters:
    ----------
    geoseries : geopandas.GeoSeries
        A GeoSeries containing shapely.geometry.Point objects.
    seed : int, optional
        A seed for the random number generator.

    Returns:
    -------
    SetPoints
        A new SetPoints object.

    Raises:
    ------
    TypeError
        If geoseries is not a geopandas.GeoSeries.
    ValueError
        If geoseries is empty or contains non-Point geometries.
    """
    gpd, Point = _require_gis_dependencies()

    if not isinstance(geoseries, gpd.GeoSeries):
        raise TypeError("Input 'geoseries' must be a geopandas.GeoSeries.")

    if geoseries.empty:
        raise ValueError("Input 'geoseries' cannot be empty.")

    if not all(isinstance(geom, Point) for geom in geoseries):
        raise ValueError(
            "All geometries in 'geoseries' must be shapely.geometry.Point instances."
        )

    coords = np.array([(point.x, point.y) for point in geoseries])
    return cls(coords, seed=seed)


# METHODS
