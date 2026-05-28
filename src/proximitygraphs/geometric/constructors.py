"""Constructor functions attached to ``GeometricGraph``."""

import igraph as ig

from ..points import SetPoints


def complete(cls, setpoints):
    """Return the complete graph on the given set of points."""
    if not isinstance(setpoints, SetPoints):
        raise TypeError("Input 'setpoints' must be an instance of SetPoints.")
    complete_graph_instance = cls.__new__(cls)
    complete_graph_instance._GeometricGraph__setpoints = setpoints
    complete_graph_instance._GeometricGraph__graph = ig.Graph.Full(n=setpoints.n)
    complete_graph_instance._GeometricGraph__m = (
        complete_graph_instance._GeometricGraph__graph.ecount()
    )
    complete_graph_instance._GeometricGraph__add_lengths()
    complete_graph_instance._GeometricGraph__name = "Complete Graph"
    complete_graph_instance._GeometricGraph__details = f"K_{setpoints.n}"
    return complete_graph_instance


def from_graph(cls, graph, points, name=None):
    """Construct a GeometricGraph from an existing igraph.Graph and a set of points."""
    setpoints_instance = SetPoints(points)
    if graph.vcount() != setpoints_instance.n:
        raise ValueError("Number of vertices in graph must match number of points.")
    geometric_graph_instance = cls.__new__(cls)
    geometric_graph_instance._GeometricGraph__setpoints = setpoints_instance
    geometric_graph_instance._GeometricGraph__graph = graph.copy()
    if name is None:
        geometric_graph_instance._GeometricGraph__name = "Imported Graph"
    else:
        geometric_graph_instance._GeometricGraph__name = name
    geometric_graph_instance._GeometricGraph__details = (
        "Constructed from existing igraph.Graph"
    )
    geometric_graph_instance._GeometricGraph__m = (
        geometric_graph_instance._GeometricGraph__graph.ecount()
    )
    geometric_graph_instance._GeometricGraph__add_lengths()
    return geometric_graph_instance


def random_graph(cls, setpoints, p: float, seed: int | None = None):
    """Return a random graph on the given set of points."""
    if not isinstance(setpoints, SetPoints):
        raise TypeError("Input 'setpoints' must be an instance of SetPoints.")
    if not (0.0 <= p <= 1.0):
        raise ValueError("Connection probability 'p' must be in the range [0, 1].")
    instance = cls.__new__(cls)
    instance._GeometricGraph__setpoints = setpoints
    instance._GeometricGraph__graph = ig.Graph.Erdos_Renyi(
        n=setpoints.n, p=p, directed=False, loops=False
    )
    instance._GeometricGraph__m = instance._GeometricGraph__graph.ecount()
    instance._GeometricGraph__add_lengths()
    instance._GeometricGraph__name = "Random Graph"
    details_str = f"G({setpoints.n}, p={p:.3g}"
    if seed is not None:
        details_str += f", seed={seed}"
    details_str += ")"
    instance._GeometricGraph__details = details_str
    return instance
