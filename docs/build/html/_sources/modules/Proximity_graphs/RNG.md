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

## Example

```python
import proximitygraphs as pg

pts = pg.SetPoints.uniform_square(n=200, seed=42)

G_mst = pg.MST(pts)
G_rng = pg.RNG(pts, closed=False)
G_gg  = pg.GG(pts, closed=True)

graphs = [G_mst, G_rng, G_gg]

pg.draw_grid(graphs, 1, 3, figsize=(15, 5), details=True)
```


![Example graphs](images/rng.png)

