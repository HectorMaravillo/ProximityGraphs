# Voronoi Diagram


Constructs the Voronoi site-adjacency graph of a point set.

The Voronoi diagram partitions the plane into regions containing all locations closest to each input point. This graph connects two original input points whenever their Voronoi regions share a ridge.

## Constructor

```python
Voronoi(setpoints)
```

**Parameters:**
- **setpoints** (SetPoints): The set of points used to build the Voronoi diagram.

### Mathematical Definition:

For a set of points $P = \{p_1, p_2, \ldots, p_n\} \subset \mathbb{R}^d$, the Voronoi cell of $p_i$ is:

$$V_i = \{x \in \mathbb{R}^d : \|x - p_i\| \leq \|x - p_j\| \ \forall j \neq i\}$$

The Voronoi site-adjacency graph contains an edge $(p_i, p_j)$ when $V_i$ and $V_j$ share a ridge.

**Properties:**
- Dual of the Delaunay triangulation in general position
- Stores edges between original input points, not between Voronoi vertices
- Uses `scipy.spatial.Voronoi.ridge_points` as the edge source

**Value Errors:**
- Raises `QhullError` if there are too few points or the points are degenerate for Qhull.

## Example

```python
import proximitygraphs as pg

pts = pg.SetPoints.uniform_square(n=200, seed=42)

G = pg.Voronoi(pts)
G.draw(figsize=(7, 7), details=True)
```


![Example graphs](images/voronoi.svg)
