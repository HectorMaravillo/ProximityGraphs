# `random_graph(setpoints, p, seed=None)` [classmethod]

Creates an Erdős-Rényi random graph G(n, p).

Each possible edge is included independently with probability p.

## Parameters

- **setpoints** (SetPoints): An instance of SetPoints containing the vertex coordinates.
- **p** (float): Edge probability, must be in [0, 1].
- **seed** (int, optional): Random seed for reproducibility.

## Raises

- **TypeError**: If setpoints is not an instance of SetPoints.
- **ValueError**: If p is not in the range [0, 1].

## Returns

A GeometricGraph representing a random graph.

## Example

```python
from proximitygraphs.points import SetPoints
from proximitygraphs.geometricgraphs import GeometricGraph

# Create points
points = SetPoints.uniform_square(n=30, seed=1)

# Create random graphs with different edge probabilities
sparse = GeometricGraph.random_graph(points, p=0.1, seed=42)
dense = GeometricGraph.random_graph(points, p=0.5, seed=42)

print(f"Sparse graph: {sparse.m} edges")
print(f"Dense graph: {dense.m} edges")
```
