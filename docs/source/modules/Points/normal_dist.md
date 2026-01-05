# normal_dist

Generate a random sample of points from the bivariate standard normal N(0, I2).

Points follow a 2D Gaussian distribution centered at the origin with independent standard normal components.
Draw X in R^2 with mean vector 0 and covariance matrix I2. Components are independent with unit variance.

## Parameters

- `n` (int): The number of points to generate.
- `seed` (int): A seed for the random number generator.

## Returns

- `SetPoints`: Instance with points of shape (n, 2) following N(0, I2).

## Example

```python
from proximitygraphs.points import SetPoints

# Create a SetPoints object with 10 points from a 2D normal distribution
normal_points = SetPoints.normal_dist(n=150, seed=21)
normal_points.draw(figsize=(8, 8), v_color='purple')
```