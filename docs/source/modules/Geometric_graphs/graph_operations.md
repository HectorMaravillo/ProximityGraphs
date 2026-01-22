# Graph Operations

## `union(other)`

Computes the union of two geometric graphs.

The union contains all edges present in either graph. Both graphs must be defined on the same point set.

### Parameters

- **other** (GeometricGraph): Another geometric graph with the same vertices.

### Returns

- **GeometricGraph**: A new graph containing the union of edges.

### Raises

- **TypeError**: If other is not a GeometricGraph.
- **ValueError**: If graphs don't have the same point sets.

### Example

```python
from proximitygraphs.proximitygraphs import GG, RNG
from proximitygraphs.points import SetPoints

points = SetPoints.uniform_square(n=50, seed=1)

gabriel = GG(points)
rng = RNG(points)

# Union combines edges from both graphs
union_graph = gabriel.union(rng)
print(f"Gabriel: {gabriel.m} edges")
print(f"RNG: {rng.m} edges")
print(f"Union: {union_graph.m} edges")

union_graph.draw(figsize=(8, 8))
```

---

## `intersection(other)`

Computes the intersection of two geometric graphs.

The intersection contains only edges present in both graphs.

### Parameters

- **other** (GeometricGraph): Another geometric graph with the same vertices.

### Returns

- **GeometricGraph**: A new graph containing only common edges.

### Raises

- **TypeError**: If other is not a GeometricGraph.
- **ValueError**: If graphs don't have the same point sets.

### Example

```python
from proximitygraphs.proximitygraphs import GG, DelaunayG
from proximitygraphs.points import SetPoints

points = SetPoints.uniform_square(n=50, seed=1)

gabriel = GG(points)
delaunay = DelaunayG(points)

# Intersection contains only shared edges
intersection_graph = gabriel.intersection(delaunay)
print(f"Gabriel: {gabriel.m} edges")
print(f"Delaunay: {delaunay.m} edges")
print(f"Intersection: {intersection_graph.m} edges")
```

---

## `difference(other)`

Computes the difference of two geometric graphs (self - other).

The result contains edges in self but not in other.

### Parameters

- **other** (GeometricGraph): Another geometric graph with the same vertices.

### Returns

- **GeometricGraph**: A new graph with edges from self minus edges from other.

### Raises

- **TypeError**: If other is not a GeometricGraph.
- **ValueError**: If graphs don't have the same point sets.

### Example

```python
from proximitygraphs.proximitygraphs import DelaunayG, GG
from proximitygraphs.points import SetPoints

points = SetPoints.uniform_square(n=50, seed=1)

delaunay = DelaunayG(points)
gabriel = GG(points)

# Find edges in Delaunay but not in Gabriel
diff_graph = delaunay.difference(gabriel)
print(f"Delaunay: {delaunay.m} edges")
print(f"Gabriel: {gabriel.m} edges")
print(f"Difference: {diff_graph.m} edges")
```

---

## `symmetric_difference(other)`

Computes the symmetric difference of two geometric graphs.

The result contains edges present in exactly one of the two graphs.

### Parameters

- **other** (GeometricGraph): Another geometric graph with the same vertices.

### Returns

- **GeometricGraph**: A new graph with edges in one graph but not both.

### Raises

- **TypeError**: If other is not a GeometricGraph.
- **ValueError**: If graphs don't have the same point sets.

### Example

```python
from proximitygraphs.proximitygraphs import GG, RNG
from proximitygraphs.points import SetPoints

points = SetPoints.uniform_square(n=50, seed=1)

gabriel = GG(points)
rng = RNG(points)

# Symmetric difference: edges in exactly one graph
sym_diff = gabriel.symmetric_difference(rng)
print(f"Gabriel: {gabriel.m} edges")
print(f"RNG: {rng.m} edges")
print(f"Symmetric difference: {sym_diff.m} edges")
```

---

## `recovering(other, distance="R")`

Computes a recovery distance metric between two graphs.

This measures the dissimilarity between two graphs based on their edge sets.

### Parameters

- **other** (GeometricGraph): Another geometric graph to compare.
- **distance** (str, optional): Distance metric to use. Currently only "R" is supported, which computes the ratio |symmetric_difference| / |union|. Default "R".

### Returns

- **float**: Distance value between 0 (identical) and 1 (completely different).

### Raises

- **TypeError**: If other is not a GeometricGraph.
- **NotImplementedError**: If distance type is not supported.

### Example

```python
from proximitygraphs.proximitygraphs import GG, RNG, DelaunayG
from proximitygraphs.points import SetPoints

points = SetPoints.uniform_square(n=100, seed=1)

gabriel = GG(points)
rng = RNG(points)
delaunay = DelaunayG(points)

# Compare graphs using recovery distance
print(f"Distance Gabriel-RNG: {gabriel.recovering(rng):.4f}")
print(f"Distance Gabriel-Delaunay: {gabriel.recovering(delaunay):.4f}")
print(f"Distance RNG-Delaunay: {rng.recovering(delaunay):.4f}")
```
