# Vizualization

## code

`draw(figsize=(6,6), v_size=3, v_color='#00072D', v_alpha=1, e_size=1, e_color='#0A2472', e_alpha=1, title=True, fontsize=10, details=False, axis=False, save=None, *, fig_kwargs=None, v_kwargs=None, e_kwargs=None, title_kwargs=None, savefig_kwargs=None)`
Draws the geometric graph using Matplotlib.

This method provides flexible visualization with extensive customization options for vertices, edges, and layout.

### Parameters

- **figsize** (tuple, optional): Figure size in inches. Default (6, 6).
- **v_size** (float, optional): Vertex marker size. Set to 0 to hide vertices. Default 3.
- **v_color** (str, optional): Vertex color. Default '#00072D' (dark blue).
- **v_alpha** (float, optional): Vertex transparency [0,1]. Default 1.
- **e_size** (float, optional): Edge line width. Default 1.
- **e_color** (str, optional): Edge color. Default '#0A2472' (blue).
- **e_alpha** (float, optional): Edge transparency [0,1]. Default 1.
- **title** (bool, optional): Whether to display title. Default True.
- **fontsize** (float, optional): Title font size. Default 10.
- **details** (bool, optional): Whether to append graph details to title. Default False.
- **axis** (bool, optional): Whether to show axes. Default False.
- **save** (str, optional): If provided, saves figure as save+".png". Default None.

### Other Parameters

- **fig_kwargs** (dict): Additional arguments for matplotlib.pyplot.subplots
- **v_kwargs** (dict): Additional arguments for vertex scatter plot
- **e_kwargs** (dict): Additional arguments for edge line collection
- **title_kwargs** (dict): Additional arguments for title
- **savefig_kwargs** (dict): Additional arguments for savefig

### Returns

- **(fig, ax)**: Matplotlib figure and axes objects.

### Example

```python
from proximitygraphs.proximitygraphs import DelaunayG
from proximitygraphs.points import SetPoints

points = SetPoints.uniform_square(n=50, seed=42)
delaunay = DelaunayG(points)

# Basic visualization
fig, ax = delaunay.draw()

# Customized visualization
fig, ax = delaunay.draw(
    figsize=(10, 10),
    v_size=50,
    v_color='red',
    v_alpha=0.7,
    e_size=2,
    e_color='blue',
    e_alpha=0.5,
    title=True,
    details=True,
    axis=True
)

# Save to file
delaunay.draw(save='my_delaunay_graph')
```
## code

 `draw_orientation(num_bins=36, figsize=(5,5), color="darkgreen", area=False, component="auto")`

Creates a polar histogram showing the distribution of edge orientations.

This is particularly useful for analyzing directional patterns and anisotropy in geometric graphs.

### Parameters

- **num_bins** (int, optional): Number of angular bins. Default 36 (10° bins).
- **figsize** (tuple, optional): Figure size in inches. Default (5, 5).
- **color** (str, optional): Bar color. Default "darkgreen".
- **area** (bool, optional): If True, bar heights represent √frequency (area-proportional). If False, heights are frequencies. Default False.
- **component** (str, optional): For 3D graphs, which component to plot:
  - "auto": Automatically selects azimuth for 3D
  - "azimuth": Horizontal angle
  - "elevation": Vertical angle
  Default "auto".

### Returns

- **(fig, ax)**: Matplotlib figure and axes objects with polar projection.

### Example

```python
from proximitygraphs.proximitygraphs import DelaunayG
from proximitygraphs.points import SetPoints

# Create points from a grid (will have structured orientations)
points = SetPoints.grid(shape=(10, 10))

delaunay = DelaunayG(points)

# Plot orientation distribution
fig, ax = delaunay.draw_orientation(
    num_bins=36,
    figsize=(8, 8),
    color='blue',
    area=True
)
```