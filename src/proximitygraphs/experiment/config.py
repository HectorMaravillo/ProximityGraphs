"""Configuration helpers for ``Experiment``."""

import warnings
from collections.abc import Callable
from typing import Any

from ..geometricgraphs import GeometricGraph


def _validate_config(self):
    """Validate experiment configuration."""
    if not self.point_config:
        warnings.warn(
            "No point configuration provided. Use add_point_config().", stacklevel=2
        )

    if not self.graph_configs:
        warnings.warn(
            "No graph configurations provided. Use add_graph_config().",
            stacklevel=2,
        )

    if self.n_simulations < 1:
        raise ValueError("n_simulations must be at least 1.")

    # Validate point config structure
    if self.point_config:
        if "method" not in self.point_config:
            raise ValueError("point_config must contain 'method' key.")
        if "params" not in self.point_config:
            self.point_config["params"] = {}

    # Validate graph configs structure
    for i, gc in enumerate(self.graph_configs):
        if "class" not in gc:
            raise ValueError(f"graph_configs[{i}] must contain 'class' key.")
        if "params" not in gc:
            gc["params"] = {}
        if "name" not in gc:
            gc["name"] = gc["class"].__name__


def add_point_config(
    self,
    method: str,
    transformations: list[dict[str, Any]] | None = None,
    **params,
):
    """
    Add or update point generation configuration.

    Parameters
    ----------
    method : str
        Name of SetPoints class method (e.g., 'uniform_square', 'normal_dist').
    transformations : list of dict, optional
        List of transformations to apply after point generation. Each dict
        must contain:
        - 'method': str, name of transformation method ('rotation',
          'scaling', 'traslation', 'perturb')
        - 'params': dict, parameters for the transformation
        Example: [
            {'method': 'rotation', 'params': {'angle': 45}},
            {'method': 'scaling', 'params': {'scale': 2.0}},
            {'method': 'perturb', 'params': {'radius': 0.1}}
        ]
    **params
        Parameters to pass to the point generation method.

    Examples
    --------
    >>> # Simple point generation
    >>> exp.add_point_config('uniform_square', n=100)

    >>> # With transformations
    >>> exp.add_point_config(
    ...     'uniform_square',
    ...     n=100,
    ...     transformations=[
    ...         {'method': 'rotation', 'params': {'angle': 45}},
    ...         {'method': 'scaling', 'params': {'scale': 1.5}}
    ...     ]
    ... )

    >>> # Poisson process with perturbation
    >>> exp.add_point_config(
    ...     'poissonprocess_square',
    ...     intensity=50,
    ...     limit=1,
    ...     transformations=[
    ...         {'method': 'perturb', 'params': {'radius': 0.05}}
    ...     ]
    ... )
    """
    self.point_config = {
        "method": method,
        "params": params,
        "transformations": transformations or [],
    }
    self._validate_config()


def add_graph_config(self, graph_class, name: str | None = None, **params):
    """
    Add a graph configuration to the experiment.

    Parameters
    ----------
    graph_class : class
        Graph class reference (e.g., GG, RNG, PhysarumGraph).
    name : str, optional
        Custom name for this configuration. If None, uses class name.
    **params
        Parameters to pass to the graph constructor.

    Examples
    --------
    >>> exp.add_graph_config(pg.GG, name='Gabriel', closed=True)
    >>> exp.add_graph_config(pg.RNG, closed=False)
    >>> exp.add_graph_config(pg.PhysarumGraph, sources=[0], sinks=[50], steps=100)
    """
    config = {
        "class": graph_class,
        "params": params,
        "name": name or graph_class.__name__,
    }
    self.graph_configs.append(config)


def add_custom_metric(self, name: str, func: Callable[[GeometricGraph], float]):
    """
    Register a custom metric function.

    Parameters
    ----------
    name : str
        Name of the metric (will be used as column name in results).
    func : callable
        Function that takes a GeometricGraph and returns a numeric value.
        Signature: func(graph: GeometricGraph) -> float

    Examples
    --------
    >>> # Define custom metric
    >>> def avg_edge_length(g):
    ...     return g.lengths.mean() if g.m > 0 else 0.0
    >>>
    >>> exp.add_custom_metric('avg_edge_length', avg_edge_length)

    >>> # Define another custom metric
    >>> def clustering_coefficient(g):
    ...     return g.graph.transitivity_undirected()
    >>>
    >>> exp.add_custom_metric('clustering', clustering_coefficient)
    """
    if not callable(func):
        raise TypeError("Metric function must be callable.")
    self._custom_metrics[name] = func
