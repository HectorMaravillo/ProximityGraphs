# poissonprocess_square

Generates points according to a homogeneous Poisson point process in a square region.

## Parameters

- `intensity` (float): The intensity of the Poisson process.
- `limit` (float): The side length of the square simulation window.
- `seed` (int, optional): A seed for the random number generator.

## Returns

- `SetPoints`: A new SetPoints object.

## Example

```python
from proximitygraphs.points import SetPoints

# Create a Poisson point process in a square
set_points = SetPoints.poissonprocess_square(intensity=10, limit=1)
print(set_points.points)
```
