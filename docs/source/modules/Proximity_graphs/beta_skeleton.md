# Class: Beta_Skeleton

A parameterized family of proximity graphs where β controls the neighborhood shape.

## Constructor

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

## Mathematical Definition:

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

## Example:

```python
from proximitygraphs.points import SetPoints
from proximitygraphs.proximitygraphs import Beta_Skeleton

points = SetPoints.uniform_square(n=50, seed=42)

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

## Mathematical Definition:

Given a graph $G = (V, E)$, constructs $\text{BS}_\beta(V)$ by testing only edges in $E$ rather than all $\binom{n}{2}$ pairs:

$$\text{BS}_\beta^G(P) = \{(p, q) \in E : L_\beta(p, q) \cap P \subseteq \{p, q\}\}$$

This is much faster when $|E| \ll \binom{n}{2}$, such as when $G$ is the Delaunay triangulation.

**Value Errors:**
- Same as constructor
- Raises `TypeError` if `geom_graph` is not a `GeometricGraph`

## Example:

```python
from proximitygraphs.points import SetPoints
from proximitygraphs.proximitygraphs import Beta_Skeleton, DelaunayG

points = SetPoints.uniform_square(n=200, seed=42)

# Compute from all pairs (slow for large n)
# beta_all = Beta_Skeleton(points, beta=1.5)

# Fast: use Delaunay edges as candidates
delaunay = DelaunayG(points)
beta_fast = Beta_Skeleton.from_graph(delaunay, beta=1.5, type_region="lune")

print(f"β-skeleton from Delaunay: {beta_fast.m} edges")
print(f"Delaunay edges tested: {delaunay.m} (vs {200*199//2} all pairs)")
# Massive speedup for large point sets!
```


