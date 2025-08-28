# poissonprocess_inhomogeneus

Generates points according to an inhomogeneous Poisson point process in a square region using thinning.

## Parameters

- `fun_lambda` (callable): A function that takes two arguments (x, y coordinates) and returns the intensity of the Poisson process at that point.
- `limit` (float): The side length of the square simulation window.
- `seed` (int, optional): A seed for the random number generator.

## Returns

- `SetPoints`: A new SetPoints object.

## Example

```python
from proximitygraphs.points import SetPoints

# Define an intensity function
fun_lambda = lambda x, y: x + y

# Create an inhomogeneous Poisson point process
set_points = SetPoints.poissonprocess_inhomogeneus(fun_lambda=fun_lambda, limit=1)
print(set_points.points)
```