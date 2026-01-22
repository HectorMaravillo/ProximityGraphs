# K_Nearest_Neighbors

Connects each point to its k nearest neighbors.

## Constructor

```python
K_Nearest_Neighbors(setpoints, k, closed=False)
```

**Parameters:**
- **setpoints** (SetPoints): The set of points.
- **k** (int): Number of nearest neighbors (must be $1 \leq k < n$).
- **closed** (bool): If False (default), ignores ties. If True, includes all points at distance equal to the k-th neighbor.

## Mathematical Definition:

For each point $p \in P$, let $N_k(p)$ denote the $k$ nearest neighbors of $p$ (excluding $p$ itself). The k-nearest neighbors graph is:

$$\text{kNN}(P, k) = \{(p, q) : q \in N_k(p) \text{ or } p \in N_k(q)\}$$

Note: This is typically a directed graph, but this implementation creates undirected edges (symmetric).

The distance to the k-th nearest neighbor of $p$ is:

$$d_k(p) = \min\{r : |B(p, r) \cap P| \geq k + 1\}$$

where $B(p, r) = \{q \in P : \|q - p\| \leq r\}$.

**Properties:**
- Always has at least $kn/2$ edges (if symmetric)
- Graph is typically connected for $k \geq \log n$
- Can have up to $kn$ directed edges
- Useful for clustering and manifold learning
- Can be computed in $O(n \log n)$ using kd-trees

**Value Errors:**
- Raises `ValueError` if $k < 1$ or $k \geq n$
- Raises `TypeError` if `k` is not an integer
- Raises `TypeError` if `closed` is not boolean

## Example:

```python
from proximitygraphs.points import SetPoints
from proximitygraphs.proximitygraphs import K_Nearest_Neighbors

points = SetPoints.uniform_square(n=100, seed=42)

# Different k values
knn_3 = K_Nearest_Neighbors(points, k=3)
knn_5 = K_Nearest_Neighbors(points, k=5)
knn_10 = K_Nearest_Neighbors(points, k=10)

print(f"k=3: {knn_3.m} edges, {knn_3.cc} components")
print(f"k=5: {knn_5.m} edges, {knn_5.cc} components")
print(f"k=10: {knn_10.m} edges, {knn_10.cc} components")
# Output: k=3: ~150 edges, k=5: ~250 edges, k=10: ~500 edges

# Verify connectivity for different k
for k in [1, 2, 3, 5, 10]:
    knn = K_Nearest_Neighbors(points, k=k)
    print(f"k={k}: connected = {knn.cc == 1}")

# Average degree
print(f"k=5 average degree: {2 * knn_5.m / points.n:.2f}")
# Should be close to 2*k = 10

# Visualize
knn_5.draw(figsize=(8, 8), e_color='orange', e_size=1)
```