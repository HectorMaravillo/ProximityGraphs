# normal_dist

Generates a random sample of points from a multivariate standard normal distribution.

## Parameters

- `n` (int): The number of points to generate.
- `dims` (int): The number of dimensions for each point.
- `seed` (int): A seed for the random number generator.

## Returns

- `SetPoints`: A new SetPoints object.

## Example

```python
from proximitygraphs.points import SetPoints

# Create a SetPoints object with 10 points from a 2D normal distribution
set_points = SetPoints.normal_dist(n=10, dims=2)
print(set_points.points)
```