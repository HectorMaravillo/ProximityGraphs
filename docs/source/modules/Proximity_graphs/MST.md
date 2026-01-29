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

## Example

```python
import proximitygraphs as pg

pts = pg.SetPoints.uniform_square(n=200, seed=42)

G = pg.MST(pts)
G.draw(figsize=(7, 7), details=True)
```



![Example graphs](images/mst.png)

