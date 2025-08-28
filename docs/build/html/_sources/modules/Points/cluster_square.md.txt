# cluster_square

Generates points according to a Neyman-Scott cluster process in a square region.

## Parameters

- `intensity` (tuple of float): A tuple `(intensity_parent, intensity_daughter)`.
- `cluster` (dict): A dictionary specifying the cluster generation mechanism.
- `limit` (float): The side length of the square simulation window.
- `seed` (int, optional): A seed for the random number generator.

## Returns

- `SetPoints`: A new SetPoints object.

## Example

```python
from proximitygraphs.points import SetPoints

# Create a cluster process
set_points = SetPoints.cluster_square(
    intensity=(10, 10),
    cluster={"name": "Matern", "param": 0.1},
    limit=1
)
print(set_points.points)
```