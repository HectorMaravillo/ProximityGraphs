# β-Skeleton Family

## Class: Beta_Skeleton

A parameterized family of proximity graphs where β controls the neighborhood shape.

### Constructor

```python
Beta_Skeleton(setpoints, beta=1.5, type_region="lune", closed=False)
```

**Parameters:**
- **setpoints** (SetPoints): The set of points.
- **beta** (float): The β parameter (must be $\beta > 0$).
  - $\beta < 1$: Intersection of circles (requires type_region="intersection")
  - $\beta = 1$: Gabriel Graph (lune or circle)
  - $1 < \beta < 2$: Intermediate lune-shaped regions
  - $\beta = 2$: Relative Neighborhood Graph
  - $\beta > 2$: Stricter than RNG
  
- **type_region** (str): Region type:
  - "lune": Lune-shaped region (default for $\beta \geq 1$)
  - "circle": Circular region (for $\beta \geq 1$)
  - "intersection": Intersection of circles (for $\beta < 1$)
- **closed** (bool): If True, uses $\leq$ (closed region). If False, uses $<$ (open region).

**Mathematical Definition:**

For two points $p, q \in P$, the edge $(p, q)$ is in $\text{BS}_\beta(P)$ if the lune-shaped region $L_\beta(p, q)$ contains no other points from $P$.

**Lune Region ($\beta \geq 1$):**

$$L_\beta(p, q) = B\left(\frac{p + q}{2} + \frac{\beta}{2}n, \frac{\beta \|p-q\|}{2}\right) \cap B\left(\frac{p + q}{2} - \frac{\beta}{2}n, \frac{\beta \|p-q\|}{2}\right)$$

where $n$ is the unit normal to $\overrightarrow{pq}$ and $B(c, r)$ is a ball of radius $r$ centered at $c$.

**Circle Region ($\beta \geq 1$):**

$$C_\beta(p, q) = B\left(\frac{p + q}{2}, \frac{\beta \|p-q\|}{2}\right)$$

**Intersection Region ($\beta < 1$):**

$$I_\beta(p, q) = B(p, \beta \|p-q\|) \cap B(q, \beta \|p-q\|)$$

The edge $(p, q)$ exists if:

$$L_\beta(p, q) \cap P = \{p, q\} \quad \text{(for closed=False)}$$
$$L_\beta(p, q) \cap P \subseteq \{p, q\} \quad \text{(for closed=True)}$$

**Special Cases:**
- $\beta = 1, \text{lune}$: Gabriel Graph
- $\beta = 2, \text{lune}$: Relative Neighborhood Graph
- $\beta \to 0$: Approaches [Delaunay triangulation](delaunay)
- $\beta \to \infty$: Approaches nearest neighbor graph

**Value Errors:**
- Raises `ValueError` if $\beta \leq 0$
- Raises `ValueError` if `type_region` not in `["lune", "circle", "intersection"]`
- Raises `ValueError` if $\beta < 1$ and `type_region != "intersection"`
- Raises `TypeError` if `closed` is not a boolean

**Example:**

```python
from proximitygraphs.points import SetPoints
from proximitygraphs.proximitygraphs import Beta_Skeleton

points = SetPoints.uniform_square(n=50, dims=2, seed=42)

# Different β values produce different graphs
beta_0_5 = Beta_Skeleton(points, beta=0.5, type_region="intersection")
beta_1_0 = Beta_Skeleton(points, beta=1.0, type_region="lune")
beta_1_5 = Beta_Skeleton(points, beta=1.5, type_region="lune")
beta_2_0 = Beta_Skeleton(points, beta=2.0, type_region="lune")
beta_2_5 = Beta_Skeleton(points, beta=2.5, type_region="lune")

print(f"β=0.5: {beta_0_5.m} edges")
print(f"β=1.0 (Gabriel): {beta_1_0.m} edges")
print(f"β=1.5: {beta_1_5.m} edges")
print(f"β=2.0 (RNG): {beta_2_0.m} edges")
print(f"β=2.5: {beta_2_5.m} edges")
# Expected: decreasing number of edges as β increases

# Verify hierarchy: larger β means fewer edges
print(f"Hierarchy satisfied: {beta_0_5.m >= beta_1_0.m >= beta_1_5.m >= beta_2_0.m >= beta_2_5.m}")

# Compare lune vs circle regions
beta_circle = Beta_Skeleton(points, beta=1.5, type_region="circle")
print(f"β=1.5 circle: {beta_circle.m} edges (different from lune: {beta_1_5.m})")
```

## Class Method: from_graph

```python
Beta_Skeleton.from_graph(geom_graph, beta=1.5, type_region="lune", closed=False)
```

Constructs a β-skeleton using an existing graph's edges as candidates.

**Parameters:**
- **geom_graph** (GeometricGraph): Base graph providing edge candidates
- **beta** (float): The β parameter (must be $> 0$)
- **type_region** (str): Region type
- **closed** (bool): Region closure

**Returns:**
- **Beta_Skeleton**: A new β-skeleton graph

### Mathematical Definition:

Given a graph $G = (V, E)$, constructs $\text{BS}_\beta(V)$ by testing only edges in $E$ rather than all $\binom{n}{2}$ pairs:

$$\text{BS}_\beta^G(P) = \{(p, q) \in E : L_\beta(p, q) \cap P \subseteq \{p, q\}\}$$

This is much faster when $|E| \ll \binom{n}{2}$, such as when $G$ is the Delaunay triangulation.

**Value Errors:**
- Same as constructor
- Raises `TypeError` if `geom_graph` is not a `GeometricGraph`

### Example:

```python
from proximitygraphs.points import SetPoints
from proximitygraphs.proximitygraphs import Beta_Skeleton, DelaunayG

points = SetPoints.uniform_square(n=200, dims=2, seed=42)

# Compute from all pairs (slow for large n)
# beta_all = Beta_Skeleton(points, beta=1.5)

# Fast: use Delaunay edges as candidates
delaunay = DelaunayG(points)
beta_fast = Beta_Skeleton.from_graph(delaunay, beta=1.5, type_region="lune")

print(f"β-skeleton from Delaunay: {beta_fast.m} edges")
print(f"Delaunay edges tested: {delaunay.m} (vs {200*199//2} all pairs)")
# Massive speedup for large point sets!
```
## Class: GG (Gabriel Graph)

The Gabriel Graph is a β-skeleton with β=1.

Two points p and q are connected if the circle with diameter pq contains no other points.

### Constructor

```python
GG(setpoints, closed=True)
```

**Parameters:**
- **setpoints** (SetPoints): The set of points.
- **closed** (bool): If True (default), uses $\leq$. If False, uses $<$.

### Mathematical Definition: 

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

### Example:

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

## Class: RNG (Relative Neighborhood Graph)

The RNG is a β-skeleton with β=2.

Two points p and q are connected if the lune-shaped region between them contains no other points.

### Constructor

```python
RNG(setpoints, closed=False)
```

**Parameters:**
- **setpoints** (SetPoints): The set of points.
- **closed** (bool): If False (default), uses $<$. If True, uses $\leq$.

### Mathematical Definition:

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

### Example:

```python
from proximitygraphs.points import SetPoints
from proximitygraphs.proximitygraphs import RNG, GG, MST, Beta_Skeleton

points = SetPoints.uniform_square(n=50, dims=2, seed=42)

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
