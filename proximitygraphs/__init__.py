"""
Proximitygraphs
================


How to use the documentation
----------------------------
  >>> import proximitygraphs as pg


Available subpackages
---------------------
points
    Point-set abstractions (e.g. SetPoints) and related helpers.
envelops
    Enclosing-circle, hull-like and basic geometric primitives.
geometricgraphs
    Base GeometricGraph interface and generic graph utilities.
proximitygraphs
    Proximity-based graph families (Delaunay, RNG, GG, MST, unit disk,
    beta-skeletons, gamma-graphs, alpha-shapes/hulls, etc.).
biologicalgraphs
    Bio-inspired geometric graphs (PhysarumGraph, AntColonyGraph).
experiments
    Experiment helpers for constructing, running, and comparing graph
    models on shared point sets.


Graph construction examples
---------------------------
A typical workflow is:

1. Construct or load a point set via SetPoints.
2. Build one or more graphs over that point set.

Example (pseudocode)::

  >>> import proximitygraphs as pg
  >>> pts = pg.SetPoints.uniform_sphere(n=1000, dims = 2, seed=0)
  >>> G_g = pg.Gamma_Graph(pts)     # gamma-graph
  >>> G_p = pg.PhysarumGraph(pts)   # physarum-inspired graph
"""

__version__ = "0.1.0a1"

# Re-export selected symbols from submodules
# Re-export the submodules themselves
from . import (
    biologicalgraphs,
    envelops,
    experiments,
    geometricgraphs,
    points,
    proximitygraphs,
)
from .biologicalgraphs import (
    PhysarumGraph,
)
from .envelops import (
    circle_centroid,
    circle_smallest,
    circle_through_three_points,
    circle_through_two_points,
    is_in_circle,
    slope,
    smallest_circle,
    smallest_circle_helper,
    trivial_circle,
)
from .experiments import Experiment
from .geometricgraphs import (
    GeometricGraph,
    draw_grid,
    load_graph,
)
from .points import SetPoints
from .proximitygraphs import (
    GG,
    MST,
    NNG,
    RNG,
    SIG,
    Alpha_Hull,
    Alpha_Shape,
    Beta_Skeleton,
    Convex_Hull,
    DelaunayG,
    Elliptic_GabrielG,
    Gamma_Graph,
    ProximityGraph,
    Sigma_Graph,
    Stepping_Stone,
    Unit_Disk,
)

__all__ = [
    "GG",
    "MST",
    "NNG",
    "RNG",
    "SIG",
    "Alpha_Hull",
    "Alpha_Shape",
    "Beta_Skeleton",
    "Convex_Hull",
    "DelaunayG",
    "Elliptic_GabrielG",
    # experiments
    "Experiment",
    "Gamma_Graph",
    # geometricgraphs
    "GeometricGraph",
    # biologicalgraphs
    "PhysarumGraph",
    # proximitygraphs
    "ProximityGraph",
    # points
    "SetPoints",
    "Sigma_Graph",
    "Stepping_Stone",
    "Unit_Disk",
    "biologicalgraphs",
    # envelops
    "circle_centroid",
    "circle_smallest",
    "circle_through_three_points",
    "circle_through_two_points",
    "draw_grid",
    "envelops",
    "experiments",
    "geometricgraphs",
    "is_in_circle",
    "load_graph",
    # Submodules
    "points",
    "proximitygraphs",
    "slope",
    "smallest_circle",
    "smallest_circle_helper",
    "trivial_circle",
]
