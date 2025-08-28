# hexagonal

Generates points forming a hexagonal lattice in a 2D plane.

## Parameters

- `n_x` (int): Determines the extent of the hexagonal grid along an axis roughly aligned with the x-direction.
- `n_y` (int): Determines the extent of the hexagonal grid along an axis roughly aligned with the y-direction.

## Returns

- `SetPoints`: A new SetPoints object.

## Example

```python
from proximitygraphs.points import SetPoints

# Create a hexagonal lattice
set_points = SetPoints.hexagonal(n_x=3, n_y=3)
print(set_points.points)
```