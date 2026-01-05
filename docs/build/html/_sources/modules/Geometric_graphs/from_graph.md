# `from_graph(graph, points, name=None)` [classmethod]

Creates a GeometricGraph from an existing igraph.Graph and point coordinates.

This allows importing externally created graphs into the GeometricGraph framework.

## Parameters

- **graph** (igraph.Graph): An existing igraph Graph object.
- **points** (numpy.ndarray): Array of point coordinates with shape (n, dim).
- **name** (str, optional): Name for the graph. If None, uses "Imported Graph".

## Raises

- **ValueError**: If the number of vertices in the graph doesn't match the number of points.

## Returns

A GeometricGraph object constructed from the existing graph and points.

## Example

```python
import igraph as ig
import numpy as np
from proximitygraphs.geometricgraphs import GeometricGraph

# Create an igraph graph
ig_graph = ig.Graph.Famous("Petersen")

# Create corresponding points (circular layout)
n = ig_graph.vcount()
theta = np.linspace(0, 2*np.pi, n, endpoint=False)
points = np.column_stack([np.cos(theta), np.sin(theta)])

# Import into GeometricGraph
geom_graph = GeometricGraph.from_graph(ig_graph, points, name="Petersen Graph")
geom_graph.draw(figsize=(8, 8))
```
