"""Gabriel graph construction.

This module implements the Gabriel graph, a classical empty-region proximity
graph. Two points p and q are connected when the disk having segment pq as its
diameter contains no other sites. In the beta-skeleton family, this is the
beta=1 special case.

References
----------
Gabriel, K. R., & Sokal, R. R. (1969). A new statistical approach to
geographic variation analysis. Systematic Zoology, 18(3), 259-278.

Matula, D. W., & Sokal, R. R. (1980). Properties of Gabriel graphs relevant
to geographic variation research and the clustering of points in the plane.
Geographical Analysis, 12(3), 205-222.
"""

from .beta import Beta_Skeleton


class GG(Beta_Skeleton):
    """
    Gabriel Graph (GG) construction.

    Two points p and q are connected if the circle with diameter pq contains no
    other points. It is a special case of the beta-skeleton with beta=1 and
    circle-shaped regions.
    It is a special case of the lune-shaped beta-skeleton with beta=1.

    Attributes
    ----------
    name : str
        The name of the graph, set to "Gabriel Graph".
    details : str
        Additional information including closed.
    """

    # CONSTRUCTOR
    def __init__(self, setpoints, closed=True):
        Beta_Skeleton.__init__(self, setpoints, beta=1, closed=closed)
        self.name = "Gabriel Graph"
        self.details = f"closed={closed}"
