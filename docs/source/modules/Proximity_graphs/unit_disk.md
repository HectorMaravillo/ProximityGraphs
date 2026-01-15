# Class: Unit_Disk

The Unit Disk Graph connects points within a specified distance.

## Constructor

```python
Unit_Disk(setpoints, dist_max, closed=True)
```

**Parameters:**
- **setpoints** (SetPoints): The set of points.
- **dist_max** (float): Maximum distance for connectivity (must be $\geq 0$).
- **closed** (bool): If True (default), uses $\leq$ dist_max. If False, uses $<$ dist_max.

## Mathematical Definition:

The Unit Disk Graph $\text{UDG}_r(P)$ with radius $r$ contains edge $(p, q)$ if and only if:

$$\|p - q\| \leq r \quad \text{(closed case)}$$
$$\|p - q\| < r \quad \text{(open case)}$$

The graph can be represented as:

$$\text{UDG}_r(P) = \{(p, q) \in P \times P : p \neq q, \|p - q\| \leq r\}$$

**Properties:**
- Models wireless communication networks (transmission range)
- Contains at most $\binom{n}{2}$ edges
- Connectivity threshold: $r_c \approx \sqrt{\frac{\log n}{\pi n}}$ for $n$ uniform points in unit square
- Can be computed in $O(n^2)$ time naively, or $O(n \log n + m)$ using spatial data structures

**Applications:**
- Wireless network modeling
- Geographic information systems (proximity analysis)
- Collision detection
- Range queries in databases

**Value Errors:**
- Raises `ValueError` if `dist_max < 0`
- Raises `TypeError` if `dist_max` is not numeric
- Raises `TypeError` if `closed` is not boolean

## Example:

```python
from proximitygraphs.points import SetPoints
from proximitygraphs.proximitygraphs import Unit_Disk
import numpy as np

points = SetPoints.uniform_square(n=100, dims=2, seed=42)

# Different radii
udg_01 = Unit_Disk(points, dist_max=0.1)
udg_02 = Unit_Disk(points, dist_max=0.2)
udg_03 = Unit_Disk(points, dist_max=0.3)

print(f"r=0.1: {udg_01.m} edges, {udg_01.cc} components")
print(f"r=0.2: {udg_02.m} edges, {udg_02.cc} components")
print(f"r=0.3: {udg_03.m} edges, {udg_03.cc} components")
# Larger radius → more edges, fewer components

# Find connectivity threshold
for r in np.linspace(0.05, 0.5, 50):
    udg = Unit_Disk(points, dist_max=r)
    if udg.cc == 1:
        print(f"Connectivity threshold: r ≈ {r:.3f}")
        print(f"Edges at threshold: {udg.m}")
        break

# Compare open vs closed
udg_closed = Unit_Disk(points, dist_max=0.15, closed=True)
udg_open = Unit_Disk(points, dist_max=0.15, closed=False)
print(f"Closed (≤): {udg_closed.m} edges")
print(f"Open (<): {udg_open.m} edges")
# Closed typically has more edges

udg_02.draw(figsize=(8, 8), e_color='purple')
```