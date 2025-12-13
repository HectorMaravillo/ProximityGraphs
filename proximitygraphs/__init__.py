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

# Re-export selected symbols from submodules
from .points import SetPoints

from .envelops import (
    circle_centroid,
    circle_smallest,
    slope,
    is_in_circle,
    circle_through_two_points,
    circle_through_three_points,
    trivial_circle,
    smallest_circle_helper,
    smallest_circle,
)

from .geometricgraphs import (
    GeometricGraph,
    load_graph,
)

from .proximitygraphs import (
    ProximityGraph,
    DelaunayG,
    Convex_Hull,
    MST,
    Beta_Skeleton,
    Stepping_Stone,
    NNG,
    Sigma_Graph,
    Unit_Disk,
    SIG,
    RNG,
    GG,
    Elliptic_GabrielG,
    Alpha_Shape,
    Alpha_Hull,
    Gamma_Graph,
)

from .experiments import Experiment

from .biologicalgraphs import (
    PhysarumGraph,
    AntColonyGraph,
)

# Re-export the submodules themselves
from . import (
    points,
    envelops,
    geometricgraphs,
    proximitygraphs,
    experiments,
    biologicalgraphs,
)

__all__ = [
    # Submodules
    "points",
    "envelops",
    "geometricgraphs",
    "proximitygraphs",
    "experiments",
    "biologicalgraphs",

    # points
    "SetPoints",

    # envelops
    "circle_centroid",
    "circle_smallest",
    "slope",
    "is_in_circle",
    "circle_through_two_points",
    "circle_through_three_points",
    "trivial_circle",
    "smallest_circle_helper",
    "smallest_circle",

    # geometricgraphs
    "GeometricGraph",
    "load_graph",

    # proximitygraphs
    "ProximityGraph",
    "DelaunayG",
    "Convex_Hull",
    "MST",
    "Beta_Skeleton",
    "Stepping_Stone",
    "NNG",
    "Sigma_Graph",
    "Unit_Disk",
    "SIG",
    "RNG",
    "GG",
    "Elliptic_GabrielG",
    "Alpha_Shape",
    "Alpha_Hull",
    "Gamma_Graph",

    # experiments
    "Experiment",

    # biologicalgraphs
    "PhysarumGraph",
    "AntColonyGraph",
]

__version__ = "0.0.1"   