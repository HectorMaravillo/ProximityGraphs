"""Relative-neighborhood graph construction.

This module implements the relative-neighborhood graph. Two points p and q are
connected when their lune contains no other point that is closer to both sites
than they are to each other. In the beta-skeleton family, this is the beta=2
special case with lune-shaped regions.

References
----------
Toussaint, G. T. (1980). The relative neighbourhood graph of a finite planar
set. Pattern Recognition, 12(4), 261-268.

Jaromczyk, J. W., & Toussaint, G. T. (2002). Relative neighborhood graphs and
their relatives. Proceedings of the IEEE, 80(9), 1502-1517.
"""

from .beta import Beta_Skeleton


class RNG(Beta_Skeleton):
    """
    Relative Neighborhood Graph (RNG) construction.

    Two points p and q are connected if the lune defined by p and q contains no
    other point that is closer to either p or q than they are to each other.
    It is a special case of the beta-skeleton with beta=2 and lune-shaped regions.

    Attributes
    ----------
    name : str
        The name of the graph, set to "Relative Neighborhood Graph".
    details : str
        Additional information including closed.
    """

    # CONSTRUCTOR
    def __init__(self, setpoints, closed=False):
        Beta_Skeleton.__init__(self, setpoints, beta=2, closed=closed)
        self.name = "Relative Neighborhood Graph"
        self.details = f"closed={closed}"
