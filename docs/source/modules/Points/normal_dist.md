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
import proximitygraphs as pg

pts = pg.SetPoints.normal_dist(n=300, seed=42)

pts.draw(figsize=(8, 8), v_color='#9467bd')
```

![Example point set](images/normal_dist.png)

