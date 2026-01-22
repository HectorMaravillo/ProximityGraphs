# Minimum Spanning Tree (MST)

Constructs the Euclidean Minimum Spanning Tree.

The MST connects all vertices with minimum total edge length, without cycles.

## Constructor

```python
MST(setpoints)
```

**Parameters:**
- **setpoints** (SetPoints): The set of points.

### Mathematical Definition:

For a complete graph $K_n$ with edge weights $w(p_i, p_j) = \|p_i - p_j\|$ (Euclidean distance), the MST is a spanning tree $T = (V, E_T)$ such that:

$$\sum_{e \in E_T} w(e) = \min_{T' \text{ spanning}} \sum_{e \in T'} w(e)$$

Properties:
- $|E_T| = n - 1$ (exactly $n-1$ edges for $n$ vertices)
- Acyclic and connected
- Subgraph of the Delaunay triangulation in Euclidean spaces
- Can be computed using Kruskal's or Prim's algorithm in $O(m \log m)$ time

The MST satisfies: MST $\subseteq$ RNG $\subseteq$ GG $\subseteq$ DT

**Value Errors:**
- Requires at least 2 points
- Raises `ValueError` if `setpoints` contains fewer than 2 points

## Example:**

```python
from proximitygraphs.points import SetPoints
from proximitygraphs.proximitygraphs import MST

points = SetPoints.uniform_square(n=50, seed=42)

mst = MST(points)
total_length = mst.lengths.sum()
print(f"MST total length: {total_length:.2f}")
print(f"Number of edges: {mst.m}")  # Always n-1 = 49
# Output: MST total length: 4.87, Number of edges: 49

# Verify tree property: connected and acyclic
print(f"Connected components: {mst.cc}")
print(f"Is acyclic (no cycles): {mst.m == mst.n - 1}")
# Output: Connected components: 1, Is acyclic: True

# Average edge length
print(f"Average edge length: {total_length / mst.m:.4f}")

mst.draw(figsize=(8, 8), e_color='green', e_size=2)
```
