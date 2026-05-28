"""Persistence helpers for geometric graphs."""

import igraph as ig
import numpy as np

from .base import GeometricGraph


def load_graph(path, filename):
    """
    Load a GeometricGraph from disk given a path and filename (without extension).
    Expects a .npy file for the points and a .pickle file for the graph structure.
    Returns a GeometricGraph object with the loaded data.

    Parameters
    ----------
    path : str
        The directory path where the files are stored.
    filename : str
        The base filename (without extension) for the graph files.
    Returns
    -------
    GeometricGraph
        A new GeometricGraph object initialized with the loaded data.
    """
    points = np.load(path + filename + ".npy")
    graph = ig.Graph.Read_Pickle(path + filename)
    load_graph = GeometricGraph.from_graph(graph, points)
    load_graph.name = graph["name"]
    load_graph.details = graph["details"]
    del load_graph._GeometricGraph__graph["name"]
    del load_graph._GeometricGraph__graph["details"]
    return load_graph
