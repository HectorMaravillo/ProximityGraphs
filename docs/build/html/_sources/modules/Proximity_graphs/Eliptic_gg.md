# Elliptic Gabriel Graph

A generalization of the Gabriel Graph using elliptical regions.

## Constructor

```python
Elliptic_GabrielG(setpoints, alpha=1.5, closed=True)
```

**Parameters:**
- **setpoints** (SetPoints): The set of points.
- **alpha** (float): Ellipse aspect ratio parameter (must be $\alpha \geq 1$).
  - $\alpha = 1$: Gabriel Graph (circular)
  - $\alpha > 1$: Elliptical regions
- **closed** (bool): If True (default), uses $\leq$. If False, uses $<$.

## Mathematical Definition: 

The Elliptic Gabriel Graph $\text{EGG}_\alpha(P)$ contains edge $(p, q)$ if the ellipse $E_\alpha(p, q)$ with foci at $p$ and $q$ is empty.

The ellipse is defined by:

$$E_\alpha(p, q) = \left\{r \in \mathbb{R}^d : \|r - p\| + \|r - q\| \leq \alpha \|p - q\|\right\}$$

The edge $(p, q)$ exists if:

$$E_\alpha(p, q) \cap P \subseteq \{p, q\}$$

**Properties of the ellipse:**
- Foci: $F_1 = p$, $F_2 = q$
- Major axis length: $a = \frac{\alpha \|p-q\|}{2}$
- Focal distance: $c = \frac{\|p-q\|}{2}$
- Minor axis length: $b = \frac{\|p-q\|}{2}\sqrt{\alpha^2 - 1}$
- Eccentricity: $e = \frac{1}{\alpha}$

**Properties:**
- $\alpha = 1$: Reduces to Gabriel Graph (circle with diameter $pq$)
- $\alpha \to \infty$: Approaches complete graph
- $1 < \alpha < 2$: Intermediate between GG and less restrictive graphs
- Preserves some GG properties (e.g., planar in 2D)

**Value Errors:**
- Raises `ValueError` if $\alpha < 1$
- Raises `TypeError` if `alpha` is not numeric
- Raises `TypeError` if `closed` is not boolean

## Example

```python
import proximitygraphs as pg

pts = pg.SetPoints.uniform_square(n=150, seed=42)

G1 = pg.Elliptic_GabrielG(pts, alpha=1.0, closed=False)  # equals GG
G2 = pg.Elliptic_GabrielG(pts, alpha=1.5, closed=False)
G3 = pg.Elliptic_GabrielG(pts, alpha=2.0, closed=False)

graphs = [G1, G2, G3]
pg.draw_grid(graphs, 1, 3, figsize=(15, 5), details=True)
```


![Example graphs](images/eliptic_gg.png)

