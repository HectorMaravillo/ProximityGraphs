"""Base class for biologically inspired graph models.

Biological graph constructors in this package represent adaptive or
self-organizing networks rather than purely static empty-region proximity
rules. They are intended for models where edge strength, growth, pruning, or
transport feedback changes the graph structure.

References
----------
Tero, A., Takagi, S., Saigusa, T., Ito, K., Bebber, D. P., Fricker, M. D.,
Yumiki, K., Kobayashi, R., & Nakagaki, T. (2010). Rules for biologically
inspired adaptive network design. Science, 327(5964), 439-442.
"""

from ..geometricgraphs import GeometricGraph


class BiologicalGraph(GeometricGraph):
    """
    Base class for biologically-inspired adaptive or self-organizing networks.
    Extends GeometricGraph with the idea of dynamic evolution over time.
    """

    def __init__(self, setpoints):
        super().__init__(setpoints)
        self.name = "Biological Graph"
        self.details = "Base biological structure"

    def evolve(self, steps=100):
        raise NotImplementedError("Subclasses must implement evolve()")
