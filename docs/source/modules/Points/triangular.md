# triangular

Generates points forming a triangular lattice in a 2D plane.

## Parameters

- `n_x` (int): Determines the extent of the triangular grid along the x-direction.
- `n_y` (int): Determines the extent of the triangular grid along the y-direction.

## Returns

- `SetPoints`: A new SetPoints object.

## Example

```python
from proximitygraphs.points import SetPoints

# Create a triangular lattice
set_points = SetPoints.triangular(n_x=3, n_y=3)
print(set_points.points)
```