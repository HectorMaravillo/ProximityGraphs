# Instance Methods

## `copy()`

Creates a deep copy of the GeometricGraph.

### Returns

A new GeometricGraph object with the same structure and properties.

### Example

```python
from proximitygraphs.proximitygraphs import GG
from proximitygraphs.points import SetPoints

points = SetPoints.uniform_square(n=50, seed=1)
original = GG(points)

# Create a copy
duplicate = original.copy()
print(f"Original: {original.m} edges, Copy: {duplicate.m} edges")
```

---
## `entropy(variable_name, bins=10)`

Calculates the Shannon entropy of a graph property distribution.

Entropy measures the uncertainty or randomness in a distribution. Higher entropy indicates more uniform distribution.

### Parameters

- **variable_name** (str): The variable to analyze. Options:
  - 'orientation': Entropy of edge orientations
  - 'length': Entropy of edge lengths
  - 'degree': Entropy of vertex degrees
- **bins** (int, optional): Number of bins for histogram. Default 10.

### Returns

- **float**: Shannon entropy in bits (using base-2 logarithm).

### Raises

- **ValueError**: If variable_name is not supported.

### Example

```python
from proximitygraphs.proximitygraphs import GG, RNG
from proximitygraphs.points import SetPoints

points = SetPoints.uniform_square(n=100, seed=1)

gabriel = GG(points)
rng = RNG(points)

# Compare entropy of different properties
print(f"Gabriel Graph:")
print(f"  Orientation entropy: {gabriel.entropy('orientation', bins=36):.3f}")
print(f"  Length entropy: {gabriel.entropy('length', bins=10):.3f}")
print(f"  Degree entropy: {gabriel.entropy('degree'):.3f}")

print(f"\nRNG:")
print(f"  Orientation entropy: {rng.entropy('orientation', bins=36):.3f}")
print(f"  Length entropy: {rng.entropy('length', bins=10):.3f}")
print(f"  Degree entropy: {rng.entropy('degree'):.3f}")
```

