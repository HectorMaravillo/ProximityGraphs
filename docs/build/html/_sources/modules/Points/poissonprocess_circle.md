# poissonprocess_circle

Generates points according to a homogeneous Poisson point process on the circumference of a circle.

This method simulates points positioned on the perimeter of a circle with uniform intensity along the circumference.

The generation process:
1. The number of points N is drawn from a Poisson distribution with mean L = intensity × length, where length = 2πr (circumference).
2. Given N points, their angular positions θ are drawn independently from U(0, 2π).
3. Convert to Cartesian coordinates: x = r cos(θ), y = r sin(θ).


## Parameters

- **intensity** (float): The intensity (λ) representing the average number of points per unit length along the circumference. Must be positive.
- **radius** (float): The radius of the circle. Must be positive.
- **seed** (int, optional): A seed for the random number generator. If None, uses entropy from the OS.


## Returns

- `SetPoints`: Instance with points randomly distributed on the circle's circumference.

## Example

```python
import proximitygraphs as pg

pts = pg.SetPoints.poissonprocess_circle(intensity=150, radius=1, seed=7)

pts.draw(figsize=(8, 8), v_color='#17becf')
```

![Example point set](images/poissonprocess_circle.png)

