# from_geopandas

Creates a SetPoints object from a geopandas.GeoSeries of Points.

## Parameters

- `geoseries` (geopandas.GeoSeries): A GeoSeries containing shapely.geometry.Point objects.
- `seed` (int, optional): A seed for the random number generator.

## Returns

- `SetPoints`: A new SetPoints object.

## Example

```python
import geopandas as gpd
from shapely.geometry import Point
from proximitygraphs.points import SetPoints

# Create a GeoSeries of points
gs = gpd.GeoSeries([Point(1, 1), Point(2, 2), Point(3, 3)])

# Create a SetPoints object from the GeoSeries
set_points = SetPoints.from_geopandas(gs)
print(set_points.points)
```