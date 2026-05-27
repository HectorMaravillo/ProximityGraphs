"""Graph set-operation functions attached to ``GeometricGraph``."""

import igraph as ig
import numpy as np


def _base_graph_class(instance):
    """Find the base GeometricGraph class in the instance MRO."""
    for cls in type(instance).mro():
        if cls.__name__ == "GeometricGraph":
            return cls
    raise TypeError("Could not find GeometricGraph in the instance MRO.")


def _prepare_graphs_for_operation(self, other_graph_obj):
    graph_a_copy = self.graph.copy()
    graph_b_copy = other_graph_obj.graph.copy()
    for g_copy in [graph_a_copy, graph_b_copy]:
        if "name" not in g_copy.vertex_attributes():
            g_copy.vs["name"] = [f"v{i}" for i in range(g_copy.vcount())]
        attrs_to_delete = [
            attr for attr in g_copy.vertex_attributes() if attr != "name"
        ]
        for vattr in attrs_to_delete:
            del g_copy.vs[vattr]
    return graph_a_copy, graph_b_copy


def _check_setpoints_compatibility(self, other):
    if not isinstance(other, _base_graph_class(self)):
        raise TypeError("Input 'other' must be an instance of GeometricGraph.")
    if not (self.n == other.n and np.array_equal(self.points, other.points)):
        raise ValueError(
            "Graphs must be defined on the same point sets for this operation."
        )


def union(self, other):
    """Return a new GeometricGraph that is the union of self and other."""
    self._check_setpoints_compatibility(other)
    graph_a, graph_b = self._prepare_graphs_for_operation(other)
    union_igraph = ig.union([graph_a, graph_b], byname=False)
    union_g = _base_graph_class(self)(self.setpoints)
    union_g._GeometricGraph__graph = union_igraph
    union_g._GeometricGraph__m = union_igraph.ecount()
    union_g._GeometricGraph__add_lengths()
    union_g.name = f"Union of ({self.name}) and ({other.name})"
    union_g.details = "Union operation"
    return union_g


def intersection(self, other):
    """Return a new GeometricGraph that is the intersection of self and other."""
    self._check_setpoints_compatibility(other)
    graph_a, graph_b = self._prepare_graphs_for_operation(other)
    intersection_igraph = ig.intersection([graph_a, graph_b], byname=False)
    intersection_g = _base_graph_class(self)(self.setpoints)
    intersection_g._GeometricGraph__graph = intersection_igraph
    intersection_g._GeometricGraph__m = intersection_igraph.ecount()
    intersection_g._GeometricGraph__add_lengths()
    intersection_g.name = f"Intersection of ({self.name}) and ({other.name})"
    intersection_g.details = "Intersection operation"
    return intersection_g


def difference(self, other):
    """Return a new GeometricGraph that is the difference of self and other
    (edges in self but not in other)."""
    self._check_setpoints_compatibility(other)
    graph_a, graph_b = self._prepare_graphs_for_operation(other)
    difference_igraph = graph_a.difference(graph_b)
    difference_g = _base_graph_class(self)(self.setpoints)
    difference_g._GeometricGraph__graph = difference_igraph
    difference_g._GeometricGraph__m = difference_igraph.ecount()
    difference_g._GeometricGraph__add_lengths()
    difference_g.name = f"Difference of ({self.name}) and ({other.name})"
    difference_g.details = "Difference operation (self - other)"
    return difference_g


def symmetric_difference(self, other):
    """Return the symmetric difference of self and other."""
    self._check_setpoints_compatibility(other)
    edges_g = set(self.graph.get_edgelist())
    edges_h = set(other.graph.get_edgelist())
    sym_diff_edges = list(edges_g.symmetric_difference(edges_h))
    symmetric_g = _base_graph_class(self)(self.setpoints)
    if sym_diff_edges:
        symmetric_g.graph.add_edges(sym_diff_edges)
    symmetric_g._GeometricGraph__m = symmetric_g.graph.ecount()
    symmetric_g._GeometricGraph__add_lengths()
    symmetric_g.name = f"Symmetric Difference of ({self.name}) and ({other.name})"
    symmetric_g.details = "Symmetric Difference operation"
    return symmetric_g


def recovering(self, other, distance="R"):
    """Return a distance between self and other based on the specified set operation."""
    if not isinstance(other, _base_graph_class(self)):
        raise TypeError("Input 'other' must be an instance of GeometricGraph.")
    union_graph = self.union(other)
    if distance == "R":
        symmetric_diff_graph = self.symmetric_difference(other)
        if union_graph.m == 0:
            return 0.0 if symmetric_diff_graph.m == 0 else 1.0
        return symmetric_diff_graph.m / union_graph.m
    else:
        raise NotImplementedError(f"Distance type '{distance}' is not supported.")
