# poissonprocess_circle

Generates points according to a homogeneous Poisson point process on the circumference of a circle.

## Parameters

- `intensity` (float): The intensity of the Poisson process.
- `radius` (float): The radius of the circle.
- `seed` (int, optional): A seed for the random number generator.

## Returns

- `SetPoints`: A new SetPoints object.

## Example

```python
from proximitygraphs.points import SetPoints

# Create a Poisson point process on a circle
set_points = SetPoints.poissonprocess_circle(intensity=10, radius=1)
print(set_points.points)
```