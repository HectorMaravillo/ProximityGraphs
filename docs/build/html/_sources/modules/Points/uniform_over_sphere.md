# uniform_over_sphere

Generate a random uniform sample of points on the unit circle S^1 ⊂ R^2.

Points are uniformly distributed on the surface of the unit circle, meaning they have equal density at every point on the circumference.

Draw Z ~ N(0, I2), then project onto the circle:
- X = Z / ||Z||₂

This produces a rotationally-invariant (uniform) distribution on S^1.

## Parameters

- `n` (int): The number of points to generate.
- `seed` (int): A seed for the random number generator.

## Returns

- `SetPoints`: Instance with points of shape (n, 2) lying on the unit circle.

## Example

```python
from proximitygraphs.points import SetPoints

# Create a SetPoints object with 10 points on a 2D circle
disk_points = SetPoints.uniform_sphere(n=200, seed=99)
disk_points.draw(figsize=(8, 8), v_color='green')
```