# Alpha_Shape

Constructs the α-shape boundary of a planar point set.

The α-shape is a generalization of the convex hull controlled by parameter α.

## Constructor

```python
Alpha_Shape(setpoints, alpha, tol=1e-12, qhull_options=None)
```

**Parameters:**
- **setpoints** (SetPoints): The set of points (must be 2D).
- **alpha** (float): Alpha parameter controlling boundary tightness.
  - $\alpha \approx 0$: Convex hull
  - $\alpha > 0$: Tighter boundary (uses furthest-site Delaunay)
  - Larger $|\alpha|$: Tighter fit to the point cloud
- **tol** (float, optional): Numerical tolerance. Default $10^{-12}$.
- **qhull_options** (str, optional): Options for Qhull. Default None.

## Mathematical Definition:

The $\alpha$-shape $S_\alpha(P)$ is defined using the $\alpha$-complex, which is a subcomplex of the Delaunay triangulation.

For $\alpha > 0$, a simplex $\sigma$ in the Delaunay triangulation is in the $\alpha$-complex if there exists an empty ball of radius $r = \frac{1}{\alpha}$ that passes through the vertices of $\sigma$ and contains no points of $P$ in its interior.

## Formal definition:

For $\alpha > 0$, let $R(\sigma)$ denote the circumradius of simplex $\sigma$. Then:

$$\sigma \in C_\alpha(P) \iff R(\sigma) \leq \frac{1}{\alpha}$$

The $\alpha$-shape is the boundary of the union of simplices in $C_\alpha(P)$.

**Properties:**
- $\alpha \to 0$: $S_\alpha(P) \to \text{conv}(P)$ (convex hull)
- $\alpha \to \infty$: $S_\alpha(P) \to P$ (individual points)
- Intermediate $\alpha$: Captures non-convex boundaries
- Useful for shape reconstruction from point clouds
- Can have multiple connected components
- Edges form the boundary of the $\alpha$-complex

**Value Errors:**
- Raises `ValueError` if `setpoints` is not 2D
- Raises `QhullError` if fewer than 3 points provided
- Raises `TypeError` if `alpha` is not numeric
- Raises `TypeError` if `tol` is not numeric

## Example:

```python
from proximitygraphs.points import SetPoints
from proximitygraphs.proximitygraphs import Alpha_Shape, Convex_Hull
import numpy as np

# Create point cloud with irregular boundary (star shape)
np.random.seed(42)
theta = np.linspace(0, 2*np.pi, 100)
r = 1 + 0.3*np.sin(5*theta)
x = r * np.cos(theta) + 0.05*np.random.randn(100)
y = r * np.sin(theta) + 0.05*np.random.randn(100)
points = SetPoints(np.column_stack([x, y]))

# Compare different α values
hull = Convex_Hull(points)
alpha_0_1 = Alpha_Shape(points, alpha=0.1)
alpha_0_5 = Alpha_Shape(points, alpha=0.5)
alpha_1_0 = Alpha_Shape(points, alpha=1.0)
alpha_2_0 = Alpha_Shape(points, alpha=2.0)

print(f"Convex Hull: {hull.m} edges")
print(f"α-Shape (0.1): {alpha_0_1.m} edges")
print(f"α-Shape (0.5): {alpha_0_5.m} edges")
print(f"α-Shape (1.0): {alpha_1_0.m} edges")
print(f"α-Shape (2.0): {alpha_2_0.m} edges")
# Smaller α (closer to convex hull) → fewer edges
# Larger α (tighter fit) → potentially more edges to capture concavities

# Visualize evolution of α
import matplotlib.pyplot as plt
fig, axes = plt.subplots(2, 2, figsize=(12, 12))

for ax, (alpha, shape) in zip(axes.flat, [
    (0.1, alpha_0_1),
    (0.5, alpha_0_5),
    (1.0, alpha_1_0),
    (2.0, alpha_2_0)
]):
    shape.draw(ax=ax, e_color='red', e_size=2, v_size=10)
    ax.set_title(f'α={alpha}, edges={shape.m}')
    ax.axis('equal')

plt.tight_layout()
plt.show()

# Check boundary property
print(f"α=1.0: {alpha_1_0.cc} component(s)")
```