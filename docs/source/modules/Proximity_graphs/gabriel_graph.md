# Gabriel Graph

The Gabriel Graph is a β-skeleton with β=1.

Two points p and q are connected if the circle with diameter pq contains no other points.

## Constructor

```python
GG(setpoints, closed=True)
```

**Parameters:**
- **setpoints** (SetPoints): The set of points.
- **closed** (bool): If True (default), uses $\leq$. If False, uses $<$.

## Mathematical Definition: 

The Gabriel Graph $\text{GG}(P)$ contains edge $(p, q)$ if and only if the closed ball with diameter $\overline{pq}$ is empty:

$$\text{GG}(P) = \left\{(p, q) : B\left(\frac{p+q}{2}, \frac{\|p-q\|}{2}\right) \cap P \subseteq \{p, q\}\right\}$$

Equivalently, $(p, q) \in \text{GG}(P)$ if:

$$\forall r \in P \setminus \{p, q\}: \|r - p\|^2 + \|r - q\|^2 \geq \|p - q\|^2$$

This is the "empty diametral circle" property.

**Properties:**
- Subgraph of the Delaunay triangulation: $\text{GG}(P) \subseteq \text{DT}(P)$
- Supergraph of RNG and MST: $\text{MST}(P) \subseteq \text{RNG}(P) \subseteq \text{GG}(P)$
- Important in wireless sensor networks (models direct communication)
- Typically has $O(n)$ edges
- Can be computed in $O(n \log n)$ time via Delaunay

**Value Errors:**
- Raises `TypeError` if `closed` is not boolean
- Requires at least 2 points

## Example:

```python
from proximitygraphs.points import SetPoints
from proximitygraphs.proximitygraphs import GG, Beta_Skeleton

points = SetPoints.uniform_square(n=50, dims=2, seed=42)

gabriel = GG(points, closed=True)
gabriel_open = GG(points, closed=False)

print(f"Gabriel (closed): {gabriel.m} edges")
print(f"Gabriel (open): {gabriel_open.m} edges")
# Closed region has more edges

# Verify Gabriel = Beta-Skeleton(beta=1)
beta_1 = Beta_Skeleton(points, beta=1.0, type_region="lune", closed=True)
print(f"β=1 lune: {beta_1.m} edges")
print(f"Match: {gabriel.m == beta_1.m}")  # Should be True

# Test empty circle property manually
edges = gabriel.graph.get_edgelist()
p = points.points
valid_count = 0
for i, j in edges[:5]:  # Check first 5 edges
    center = (p[i] + p[j]) / 2
    radius = np.linalg.norm(p[i] - p[j]) / 2
    distances = np.linalg.norm(p - center, axis=1)
    # Should have no points strictly inside
    inside = np.sum((distances < radius) & (np.arange(len(p)) != i) & (np.arange(len(p)) != j))
    if inside == 0:
        valid_count += 1
print(f"Edges satisfying empty circle: {valid_count}/5")

gabriel.draw(figsize=(8, 8))
```