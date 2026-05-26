"""
Backward-compatible imports for biologically-inspired graph constructors.

The implementations now live in ``proximitygraphs.biological``.
"""

from .biological import BiologicalGraph, FungalGraph, PhysarumGraph

__all__ = [
    "BiologicalGraph",
    "FungalGraph",
    "PhysarumGraph",
]
