# Relative Neighborhood Graph)

The RNG is a β-skeleton with β=2.

Two points p and q are connected if the lune-shaped region between them contains no other points.

## Constructor

```python
RNG(setpoints, closed=False)
```

**Parameters:**
- **setpoints** (SetPoints): The set of points.
- **closed** (bool): If False (default), uses $<$. If True, uses $\leq$.

## Mathematical Definition:

The Relative Neighborhood Graph $\text{RNG}(P)$ contains edge $(p, q)$ if and only if:

$$\forall r \in P \setminus \{p, q\}: \max(\|r - p\|, \|r - q\|) \geq \|p - q\|$$

Equivalently, the lune-shaped region $L(p, q) = B(p, \|p-q\|) \cap B(q, \|p-q\|)$ is empty:

$$L(p, q) \cap P \subseteq \{p, q\}$$

Geometrically, no point is closer to both $p$ and $q$ than they are to each other.

**Properties:**
- Subgraph of Gabriel Graph: $\text{RNG}(P) \subseteq \text{GG}(P)$
- Supergraph of MST: $\text{MST}(P) \subseteq \text{RNG}(P)$
- Contains all nearest neighbor edges
- Typically has $O(n)$ edges
- Graph is connected if MST is unique
- Maximum degree is $\leq 6n^{2/3}$ in 2D

**Value Errors:**
- Raises `TypeError` if `closed` is not boolean
- Requires at least 2 points

## Example:

```python
from proximitygraphs.points import SetPoints
from proximitygraphs.proximitygraphs import RNG, GG, MST, Beta_Skeleton

points = SetPoints.uniform_square(n=50, seed=42)

mst = MST(points)
rng = RNG(points)
gabriel = GG(points)

print(f"MST: {mst.m} edges")
print(f"RNG: {rng.m} edges")
print(f"Gabriel: {gabriel.m} edges")
print("Hierarchy: MST ⊆ RNG ⊆ Gabriel ⊆ Delaunay")
# Output: MST: 49, RNG: ~70, Gabriel: ~100

# Verify RNG = Beta-Skeleton(beta=2)
beta_2 = Beta_Skeleton(points, beta=2.0, type_region="lune", closed=False)
print(f"β=2 lune: {beta_2.m} edges")
print(f"Match with RNG: {rng.m == beta_2.m}")  # Should be True

# Verify hierarchy
print(f"MST ⊆ RNG: {mst.m <= rng.m}")
print(f"RNG ⊆ GG: {rng.m <= gabriel.m}")

# Test lune property for one edge
edges = rng.graph.get_edgelist()
i, j = edges[0]
p_i, p_j = points.points[i], points.points[j]
dist_ij = np.linalg.norm(p_i - p_j)

# Check all other points
violations = 0
for k in range(points.n):
    if k != i and k != j:
        p_k = points.points[k]
        if max(np.linalg.norm(p_k - p_i), np.linalg.norm(p_k - p_j)) < dist_ij:
            violations += 1
print(f"Lune violations for edge ({i},{j}): {violations}")  # Should be 0

rng.draw(figsize=(8, 8))
```
