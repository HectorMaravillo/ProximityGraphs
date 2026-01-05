# from_geopandas

Creates a SetPoints object from a geopandas.GeoSeries of Points.

This method allows integration with geospatial data by converting GeoPandas Point geometries into a SetPoints object.


## Parameters

- **geoseries** (geopandas.GeoSeries): A GeoSeries containing shapely.geometry.Point objects.
- **seed** (int, optional): A seed for the random number generator.


## Returns

- `SetPoints`: A new SetPoints object containing the points from the GeoSeries.


## Example


```python
import geopandas as gpd
from shapely.geometry import Point
from proximitygraphs.points import SetPoints

# Create a GeoSeries of points
points_list = [Point(i, i**2) for i in range(10)]
geo_series = gpd.GeoSeries(points_list)

# Convert to SetPoints
my_points = SetPoints.from_geopandas(geo_series, seed=42)
my_points.draw(figsize=(8, 8))
```