# grid

Generates a regular grid of points.

## Parameters

- `shape` (tuple of int): A tuple where each element specifies the number of points along that dimension.

## Returns

- `SetPoints`: A new SetPoints object.

## Example

```python
from proximitygraphs.points import SetPoints

# Create a 3x3 grid of points
set_points = SetPoints.grid(shape=(3, 3))
print(set_points.points)
```