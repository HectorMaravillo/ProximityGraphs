"""Point generation functions attached to ``SetPoints``."""

from .cluster_square import cluster_square
from .grid import grid
from .hexagonal import hexagonal
from .normal_dist import normal_dist
from .poissonprocess_circle import poissonprocess_circle
from .poissonprocess_inhomogeneus import poissonprocess_inhomogeneus
from .poissonprocess_square import poissonprocess_square
from .triangular import triangular
from .uniform_over_sphere import uniform_over_sphere
from .uniform_sphere import uniform_sphere
from .uniform_square import uniform_square

__all__ = [
    "cluster_square",
    "grid",
    "hexagonal",
    "normal_dist",
    "poissonprocess_circle",
    "poissonprocess_inhomogeneus",
    "poissonprocess_square",
    "triangular",
    "uniform_over_sphere",
    "uniform_sphere",
    "uniform_square",
]
