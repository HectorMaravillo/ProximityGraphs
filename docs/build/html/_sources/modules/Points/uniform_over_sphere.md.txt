# uniform_over_sphere

Generate a random uniform sample of points on the surface of a unit n-sphere.

## Parameters

- `n` (int): The number of points to generate.
- `dims` (int): The number of dimensions for each point.
- `seed` (int): A seed for the random number generator.

## Returns

- `SetPoints`: A new SetPoints object.

## Example

```python
from proximitygraphs.points import SetPoints

# Create a SetPoints object with 10 points on a 2D circle
set_points = SetPoints.uniform_over_sphere(n=10, dims=2)
print(set_points.points)
```