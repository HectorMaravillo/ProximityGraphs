# `complete(setpoints)` [classmethod]

Creates a complete graph where every pair of vertices is connected.

A complete graph on n vertices, denoted K_n, has n(n-1)/2 edges.

## Parameters

- **setpoints** (SetPoints): An instance of SetPoints containing the vertex coordinates.

## Raises

- **TypeError**: If setpoints is not an instance of SetPoints.

## Returns

A GeometricGraph representing the complete graph K_n.

## Example

```python
from proximitygraphs.points import SetPoints
from proximitygraphs.geometricgraphs import GeometricGraph

# Create 10 random points
points = SetPoints.uniform_square(n=10, seed=1)

# Create complete graph
complete = GeometricGraph.complete(points)
print(f"Complete graph K_{complete.n} has {complete.m} edges")  # K_10 has 45 edges

# Visualize
complete.draw(figsize=(8, 8))
```
