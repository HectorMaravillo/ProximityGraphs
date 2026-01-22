# Data Export and Conversion

## `save(path, filename)`

Saves the graph to disk using igraph's pickle format.

Saves both the graph structure and point coordinates.

### Parameters

- **path** (str): Directory path where files will be saved.
- **filename** (str): Base filename (without extension).

### Example

```python
from proximitygraphs.proximitygraphs import GG
from proximitygraphs.points import SetPoints

points = SetPoints.uniform_square(n=100, seed=1)
gabriel = GG(points)

# Save graph
gabriel.save('/tmp', 'my_gabriel_graph')
# Creates: /tmp/my_gabriel_graph and /tmp/my_gabriel_graph.npy
```

---

## `to_gpd_lines()`

Converts graph edges to a GeoDataFrame of LineString geometries.

Useful for GIS workflows and spatial analysis.

### Returns

- **GeoDataFrame**: A GeoDataFrame with one row per edge, containing:
  - geometry: LineString for each edge
  - union_initial: Start vertex index
  - union_final: End vertex index
  - All edge attributes from the graph

### Raises

- **ValueError**: If points are not 2D.

### Example

```python
from proximitygraphs.proximitygraphs import DelaunayG
from proximitygraphs.points import SetPoints

points = SetPoints.uniform_square(n=50, seed=1)
delaunay = DelaunayG(points)

# Convert to GeoDataFrame
gdf_lines = delaunay.to_gpd_lines()
print(f"GeoDataFrame shape: {gdf_lines.shape}")
print(gdf_lines.head())

# Can now use GeoPandas functionality
gdf_lines.plot(figsize=(10, 10))
```

---

## `to_gpd_polygons()`

Converts graph faces to a GeoDataFrame of Polygon geometries.

Extracts enclosed regions (faces) from the planar graph.

### Returns

- **GeoDataFrame**: A GeoDataFrame with one row per face/polygon.

### Raises

- **ValueError**: If points are not 2D.
- **TypeError**: If graph has no internal faces (e.g., it's a tree).
- **ValueError**: If polygonization fails.

### Example

```python
from proximitygraphs.proximitygraphs import DelaunayG
from proximitygraphs.points import SetPoints

points = SetPoints.uniform_square(n=30, seed=1)
delaunay = DelaunayG(points)

# Convert to polygon GeoDataFrame
gdf_polygons = delaunay.to_gpd_polygons()
print(f"Number of faces: {len(gdf_polygons)}")

# Visualize polygons
gdf_polygons.plot(figsize=(10, 10), alpha=0.5, edgecolor='black')
```

---

## Module-Level Functions

### `load_graph(path, filename)`

Loads a previously saved GeometricGraph from disk.

#### Parameters

- **path** (str): Directory path where files are located.
- **filename** (str): Base filename (without extension).

#### Returns

- **GeometricGraph**: The loaded graph.

#### Example

```python
from proximitygraphs.geometricgraphs import load_graph

# Load previously saved graph
loaded_graph = load_graph('/tmp', 'my_gabriel_graph')
print(f"Loaded graph: {loaded_graph.name}")
print(f"Vertices: {loaded_graph.n}, Edges: {loaded_graph.m}")
```