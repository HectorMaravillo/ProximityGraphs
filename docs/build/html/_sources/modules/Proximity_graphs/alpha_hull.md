# Alpha Hull

Constructs the α-hull with circular arc boundaries.

The α-hull replaces straight edges with circular arcs of radius $R = \frac{1}{|\alpha|}$.

## Constructor

```python
Alpha_Hull(setpoints, alpha, n_points_per_arc=40, tol=1e-12, qhull_options=None)
```

**Parameters:**
- **setpoints** (SetPoints): The set of points (must be 2D).
- **alpha** (float): Alpha parameter.
  - $\alpha \approx 0$: Convex hull with straight edges
  - $\alpha \neq 0$: Circular arcs with radius $R = \frac{1}{|\alpha|}$
- **n_points_per_arc** (int, optional): Samples per arc for rendering. Default 40.
- **tol** (float, optional): Numerical tolerance. Default $10^{-12}$.
- **qhull_options** (str, optional): Qhull options. Default None.

## Mathematical Definition:

The $\alpha$-hull extends the $\alpha$-shape by replacing straight boundary edges with circular arcs.

For each boundary edge $(p, q)$ in the $\alpha$-shape, the $\alpha$-hull replaces it with a circular arc of radius $R = \frac{1}{|\alpha|}$.

**Arc construction:**

Given edge $(p, q)$, the arc is part of a circle with:
- Radius: $R = \frac{1}{|\alpha|}$
- Center $c$ satisfying: $\|c - p\| = \|c - q\| = R$
- The center is on the perpendicular bisector of $\overline{pq}$

The center is located at:

$$c = \frac{p + q}{2} \pm \frac{h}{d}(q - p)^{\perp}$$

where $d = \|p - q\|$, $h = \sqrt{R^2 - (d/2)^2}$, and $(q-p)^{\perp}$ is the perpendicular vector.

The sign $\pm$ is chosen so the arc bulges outward from the point set.

**Properties:**
- $\alpha \to 0$: Reduces to convex hull (straight edges)
- $\alpha > 0$: Arcs bulge inward
- $\alpha < 0$: Arcs bulge outward
- Larger $|\alpha|$: Smaller radius, tighter fit
- Provides smooth boundary representation

**Attributes:**
- **arcs** (list): Sampled points for each circular arc
- **segments** (list): Straight edge representations for analytics

**Value Errors:**
- Raises `ValueError` if `setpoints` is not 2D
- Raises `ValueError` if $\alpha = 0$ (infinite radius)
- Raises `ValueError` if `n_points_per_arc < 2`
- Raises `TypeError` if `n_points_per_arc` is not an integer
- Raises `QhullError` if fewer than 3 points provided

## Custom Drawing

The Alpha_Hull class overrides `draw()` to render circular arcs instead of straight edges.

**Method:**

```python
Alpha_Hull.draw(figsize=(8, 8), ax=None, e_color='blue', e_size=2, v_size=20, **kwargs)
```

**Parameters:**
- **figsize** (tuple): Figure size if creating new figure
- **ax** (matplotlib.axes.Axes): Existing axes to draw on
- **e_color** (str): Edge/arc color
- **e_size** (float): Edge/arc line width
- **v_size** (float): Vertex marker size
- **kwargs**: Additional matplotlib arguments

**Implementation Detail:**

Instead of drawing straight lines between vertices, the `draw()` method:
1. Iterates through `self.arcs`
2. Plots each arc as a smooth curve using the sampled points
3. Renders vertices as scatter points

## Example

```python
import proximitygraphs as pg
import numpy as np

theta = np.linspace(0, 2*np.pi, 200, endpoint=False)
r = 1 + 0.35*np.sin(5*theta)
x = r * np.cos(theta) + 0.05*np.random.default_rng(42).standard_normal(theta.size)
y = r * np.sin(theta) + 0.05*np.random.default_rng(43).standard_normal(theta.size)
pts = pg.SetPoints(np.column_stack([x, y]))

A01 = pg.Alpha_Hull(pts, alpha=0.1)
A05 = pg.Alpha_Hull(pts, alpha=0.5)
A20 = pg.Alpha_Hull(pts, alpha=-0.5)

graphs = [A01, A05, A10, A20]
pg.draw_grid(graphs, 2, 2, figsize=(10, 10), details=True)
```



![Example graphs](images/alpha_hull.png)