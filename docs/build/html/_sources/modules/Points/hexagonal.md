# hexagonal

Generates points forming a hexagonal lattice in a 2D plane.

A hexagonal lattice is constructed as the union of two interleaved grids. Points in a hexagonal grid are centers of hexagons in a tessellation, where each point has 6 equidistant neighbors.

The method generates two offset grids:
1. **grid_1**: Base grid with x-coordinates spaced by alternating increments (1, 2, 1, 2,...) and y-coordinates spaced by √3.
2. **grid_2**: Offset grid with x-coordinates shifted by -0.5 and y-coordinates shifted by 0.5√3.

The combination produces the characteristic hexagonal pattern.

## Parameters

- **n_x** (int): Determines the extent of the hexagonal grid along the x-direction. Influences the number of columns.
- **n_y** (int): Determines the extent of the hexagonal grid along the y-direction. Influences the number of rows.

## Returns

- `SetPoints`: Instance with points forming a hexagonal lattice.

## Example

```python
import proximitygraphs as pg

pts = pg.SetPoints.hexagonal(n_x=10, n_y=10)

pts.draw(figsize=(8, 8), v_color='#ff7f0e', v_size=18)
```

![Example point set](images/hexagonal.png)

