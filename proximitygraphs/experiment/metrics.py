"""Metric extraction and aggregation helpers for ``Experiment``."""

import warnings
from typing import Any

import numpy as np
import pandas as pd

from ..geometricgraphs import GeometricGraph


def _extract_metrics(
    self, graph: GeometricGraph, simulation: int, graph_type: str
) -> dict[str, Any]:
    """Extract all metrics from a graph."""
    metrics = {
        "simulation": simulation,
        "graph_type": graph_type,
    }

    # Built-in topological metrics
    metrics["n_vertices"] = graph.n
    metrics["n_edges"] = graph.m
    metrics["n_components"] = graph.cc
    metrics["n_faces"] = graph.f

    # Degree statistics
    if graph.n > 0:
        degrees = graph.graph.degree()
        metrics["mean_degree"] = np.mean(degrees) if degrees else 0.0
        metrics["std_degree"] = np.std(degrees) if degrees else 0.0
        metrics["min_degree"] = min(degrees) if degrees else 0.0
        metrics["max_degree"] = max(degrees) if degrees else 0.0
    else:
        metrics["mean_degree"] = 0.0
        metrics["std_degree"] = 0.0
        metrics["min_degree"] = 0.0
        metrics["max_degree"] = 0.0

    # Edge length statistics
    if graph.m > 0:
        lengths = graph.lengths
        metrics["mean_length"] = float(np.mean(lengths))
        metrics["std_length"] = float(np.std(lengths))
        metrics["min_length"] = float(np.min(lengths))
        metrics["max_length"] = float(np.max(lengths))
        metrics["total_length"] = float(np.sum(lengths))
    else:
        metrics["mean_length"] = 0.0
        metrics["std_length"] = 0.0
        metrics["min_length"] = 0.0
        metrics["max_length"] = 0.0
        metrics["total_length"] = 0.0

    # Entropy metrics (if applicable)
    try:
        metrics["entropy_degree"] = graph.entropy("degree", bins=10)
    except Exception:
        metrics["entropy_degree"] = 0.0

    try:
        metrics["entropy_length"] = graph.entropy("length", bins=10)
    except Exception:
        metrics["entropy_length"] = 0.0

    try:
        metrics["entropy_orientation"] = graph.entropy("orientation", bins=36)
    except Exception:
        metrics["entropy_orientation"] = 0.0

    # Graph connectivity
    metrics["is_connected"] = graph.cc == 1

    # Density (for non-empty graphs)
    if graph.n > 1:
        max_edges = graph.n * (graph.n - 1) / 2
        metrics["density"] = graph.m / max_edges if max_edges > 0 else 0.0
    else:
        metrics["density"] = 0.0

    # Apply custom metrics
    for metric_name, metric_func in self._custom_metrics.items():
        try:
            metrics[metric_name] = float(metric_func(graph))
        except Exception as e:
            warnings.warn(f"Custom metric '{metric_name}' failed: {e}", stacklevel=2)
            metrics[metric_name] = np.nan

    return metrics


def aggregate(
    self, groupby: str = "graph_type", metrics: list[str] | None = None
) -> pd.DataFrame:
    """
    Aggregate results across simulations.

    Parameters
    ----------
    groupby : str, optional
        Column to group by. Default 'graph_type'.
    metrics : list of str, optional
        List of metric names to aggregate. If None, aggregates all numeric columns.

    Returns
    -------
    pd.DataFrame
        Aggregated statistics with mean, std, min, max for each metric.
    """
    if self.results is None:
        raise RuntimeError("No results available. Run experiment first.")

    if metrics is None:
        # Get all numeric columns except 'simulation'
        metrics = [
            col
            for col in self.results.columns
            if col not in ["simulation", "graph_type"]
            and pd.api.types.is_numeric_dtype(self.results[col])
        ]

    # Aggregate
    agg_dict = {m: ["mean", "std", "min", "max"] for m in metrics}
    self.aggregated = self.results.groupby(groupby).agg(agg_dict)

    return self.aggregated


def summary(self) -> str:
    """
    Generate a text summary of the experiment results.

    Returns
    -------
    str
        Formatted summary string.
    """
    if self.results is None:
        return "No results available. Run experiment first."

    if self.aggregated is None:
        self.aggregate()

    summary_lines = [
        f"Experiment: {self.name}",
        "=" * 60,
        f"Simulations: {self.n_simulations}",
        f"Graph types: {', '.join([gc['name'] for gc in self.graph_configs])}",
        "",
        "Aggregated Results:",
        "-" * 60,
        str(self.aggregated),
    ]

    return "\n".join(summary_lines)
