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

## Example:

```python
from proximitygraphs.points import SetPoints
from proximitygraphs.proximitygraphs import Elliptic_GabrielG, GG

points = SetPoints.uniform_square(n=50, dims=2, seed=42)

gabriel = GG(points)
elliptic_1_0 = Elliptic_GabrielG(points, alpha=1.0)  # Should equal GG
elliptic_1_5 = Elliptic_GabrielG(points, alpha=1.5)
elliptic_2_0 = Elliptic_GabrielG(points, alpha=2.0)
elliptic_3_0 = Elliptic_GabrielG(points, alpha=3.0)

print(f"Gabriel: {gabriel.m} edges")
print(f"EGG (α=1.0): {elliptic_1_0.m} edges (match: {gabriel.m == elliptic_1_0.m})")
print(f"EGG (α=1.5): {elliptic_1_5.m} edges")
print(f"EGG (α=2.0): {elliptic_2_0.m} edges")
print(f"EGG (α=3.0): {elliptic_3_0.m} edges")
# Increasing α → more edges

# Verify monotonicity
print(f"Monotonic: {elliptic_1_0.m <= elliptic_1_5.m <= elliptic_2_0.m <= elliptic_3_0.m}")

# Visualize different α values
import matplotlib.pyplot as plt
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

for ax, (alpha, graph) in zip(axes, [
    (1.0, elliptic_1_0),
    (1.5, elliptic_1_5),
    (2.0, elliptic_2_0)
]):
    graph.draw(ax=ax, e_color='blue', v_size=30)
    ax.set_title(f'α={alpha}, edges={graph.m}')

plt.tight_layout()
plt.show()
```