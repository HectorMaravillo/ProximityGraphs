# uniform_sphere

Generate a random uniform sample of points on the unit circle S^1 ⊂ R^2.

Points are uniformly distributed on the surface of the unit circle, meaning they have equal density at every point on the circumference.
Draw Z ~ N(0, I2), then project onto the circle:
- X = Z / ||Z||₂

This produces a rotationally-invariant (uniform) distribution on S^1.
## Parameters

- `n` (int): The number of points to generate.
- `seed` (int): A seed for the random number generator.

## Returns

- `SetPoints`:  new SetPoints object with points of shape (n, dims).

## Example

```python
import proximitygraphs as pg

pts = pg.SetPoints.uniform_sphere(n=200, seed=99)

pts.draw(figsize=(8, 8), v_color='#2ca02c')
```

![Example point set](images/uniform_sphere.png)

