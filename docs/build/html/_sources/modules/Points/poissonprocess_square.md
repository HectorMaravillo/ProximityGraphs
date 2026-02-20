# poissonprocess_square
Generates points according to a homogeneous Poisson point process in a square region.

A 2D homogeneous Poisson point process is characterized by a constant intensity λ (lambda), representing the average number of points per unit area.

The generation process involves two steps:
1. The number of points N is drawn from a Poisson distribution with mean L = intensity × area, where area = limit².
2. Given N points, their coordinates are drawn independently from uniform distributions U(0, limit) for both x and y.

This results in points randomly and uniformly distributed within [0, limit]².

## Parameters

- **intensity** (float): The intensity (λ) of the Poisson process, representing the average number of points per unit area. Must be positive.
- **limit** (float): The side length of the square simulation window [0, limit]². Must be positive.
- **seed** (int, optional): A seed for the random number generator to ensure reproducibility. If None, uses entropy from the OS.


## Returns

- `SetPoints`: Instance with points following a Poisson process in the square.

## Example

```python
import proximitygraphs as pg

pts = pg.SetPoints.poissonprocess_square(intensity=150, limit=1, seed=7)

pts.draw(figsize=(8, 8), v_color='#17becf')
```

![Example point set](images/poissonprocess_square.png)

