# triangular
Generates points forming a triangular lattice in a 2D plane.

A triangular lattice can be seen as the centers of a triangular tessellation of the plane, constructed by combining two offset grids.

Two grids are combined:
1. **grid_1**: Points at (i, j * √3) where i ranges from 0 to n_x and j over n_y rows.
2. **grid_2**: Offset points at (i + 0.5, (j + 0.5) * √3).

Each point in the lattice has 6 equidistant neighbors, forming equilateral triangles.

## Parameters

- **n_x** (int): Determines the extent along the x-direction. Influences the number of points in horizontal rows.
- **n_y** (int): Determines the extent along the y-direction. Influences the number of rows.

## Returns

- `SetPoints`: Instance with points forming a triangular lattice.

## Example

```python
import proximitygraphs as pg

pts = pg.SetPoints.triangular(n_x=10, n_y=10)

pts.draw(figsize=(8, 8), v_color='#d62728', v_size=18)
```

![Example point set](images/triangular.png)

