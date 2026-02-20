# poissonprocess_inhomogeneus

Generates points according to an inhomogeneous Poisson point process in a square region using the thinning algorithm.
An inhomogeneous Poisson point process is characterized by an intensity function λ(x,y) that varies spatially, determining the likelihood of finding points at different locations.

Uses the thinning (acceptance-rejection) algorithm:
1. **Find Maximum Intensity**: Numerically minimize -λ(x,y) to find λ_max = max λ(x,y) over the simulation window.
2. **Generate Homogeneous Proposal Points**: Generate N_prop ~ Poisson(λ_max × area) proposal points uniformly in [0, limit]².
3. **Thinning**: For each proposal point (x_i, y_i), keep it with probability p(x_i, y_i) = λ(x_i, y_i) / λ_max by generating u_i ~ U(0,1) and keeping the point if u_i < p(x_i, y_i).

The resulting retained points follow the inhomogeneous Poisson process defined by λ(x,y).

## Parameters

- **fun_lambda** (callable): A function taking two arguments (x, y) and returning the intensity at that point. Example: `lambda x, y: x + y`
- **n_sim** (int): This parameter is currently unused in the implementation.
- **limit** (float): The side length of the square simulation window [0, limit]².
- **seed** (int, optional): A seed for the random number generator. If None, uses entropy from the OS.
## Returns

- `SetPoints`: Instance with points following the inhomogeneous Poisson process.

## Example

```python
import proximitygraphs as pg

pts = pg.SetPoints.poissonprocess_inhomogeneus(fun_lambda=lambda x, y: x + y, limit=1, seed=7)

pts.draw(figsize=(8, 8), v_color='#8c564b')
```

![Example point set](images/poissonprocess_inhomogeneus.png)

