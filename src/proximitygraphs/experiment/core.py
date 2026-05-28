"""Experiment runner for reproducible proximity-graph simulations.

This module defines ``Experiment``, a small orchestration layer for generating
point sets, applying transformations, constructing multiple graph families, and
collecting repeated-simulation metrics in pandas data frames.

The class is intended for computational experiments: it records graph-level
statistics, supports custom metrics, aggregates repeated runs, and provides
basic plotting/export helpers for comparing geometric graph models.

References
----------
Harris, C. R., Millman, K. J., van der Walt, S. J., et al. (2020). Array
programming with NumPy. Nature, 585, 357-362.

Virtanen, P., Gommers, R., Oliphant, T. E., et al. (2020). SciPy 1.0:
Fundamental algorithms for scientific computing in Python. Nature Methods, 17,
261-272.
"""

from collections.abc import Callable
from typing import Any

import numpy as np
import pandas as pd

from .config import (
    _validate_config,
    add_custom_metric,
    add_graph_config,
    add_point_config,
)
from .metrics import _extract_metrics, aggregate, summary
from .persistence import __repr__, export_results, get_graph
from .plotting import compare_metrics, plot_metric
from .runner import _build_graph, _generate_points, run


class Experiment:
    """
    High-level API for running experiments on proximity graphs.

    This class allows you to:
    - Define point generation strategies
    - Configure multiple graph types to build on the same point sets
    - Run multiple simulations with different random seeds
    - Extract built-in metrics (degree, entropy, connectivity, etc.)
    - Define and apply custom metrics
    - Aggregate and visualize results

    Attributes
    ----------
    name : str
        Name of the experiment.
    point_config : dict
        Configuration for point generation.
    graph_configs : list of dict
        List of graph configurations to build.
    n_simulations : int
        Number of simulations to run.
    results : pd.DataFrame
        Results from all simulations.
    aggregated : pd.DataFrame
        Aggregated statistics across simulations.

    """

    def __init__(
        self,
        name: str = "Unnamed Experiment",
        point_config: dict[str, Any] | None = None,
        graph_configs: list[dict[str, Any]] | None = None,
        n_simulations: int = 30,
        seed: int | None = None,
        verbose: bool = True,
    ):
        """
        Initialize an Experiment.

        Parameters
        ----------
        name : str, optional
            Name of the experiment. Default "Unnamed Experiment".
        point_config : dict, optional
            Configuration for point generation. Must contain:
            - 'method': str, name of SetPoints class method (e.g., 'uniform_square')
            - 'params': dict, parameters to pass to the method
            - 'transformations': list of dict (optional), transformations to apply
            Example: {
                'method': 'uniform_square',
                'params': {'n': 100},
                'transformations': [
                    {'method': 'rotation', 'params': {'angle': 45}},
                    {'method': 'scaling', 'params': {'scale': 2.0}}
                ]
            }
        graph_configs : list of dict, optional
            List of graph configurations. Each dict must contain:
            - 'class': class reference (e.g., GG, RNG, PhysarumGraph)
            - 'params': dict, parameters to pass to the constructor
            - 'name': str (optional), custom name for this configuration
            Example: [{'class': GG, 'params': {'closed': True}, 'name': 'Gabriel'}]
        n_simulations : int, optional
            Number of independent simulations to run. Default 30.
        seed : int, optional
            Master random seed for reproducibility. If None, results are
            non-deterministic.
        verbose : bool, optional
            If True, print progress information. Default True.
        """
        self.name = name
        self.point_config = point_config or {}
        self.graph_configs = graph_configs or []
        self.n_simulations = n_simulations
        self.seed = seed
        self.verbose = verbose

        # Storage for results
        self.results: pd.DataFrame | None = None
        self.aggregated: pd.DataFrame | None = None
        self._raw_graphs: list[dict[str, Any]] = []

        # Custom metrics registry
        self._custom_metrics: dict[str, Callable] = {}

        # Validation
        self._validate_config()

        # Initialize random state
        if seed is not None:
            self._rng = np.random.default_rng(seed)
        else:
            self._rng = np.random.default_rng()

    _validate_config = _validate_config
    add_point_config = add_point_config
    add_graph_config = add_graph_config
    add_custom_metric = add_custom_metric
    run = run
    _generate_points = _generate_points
    _build_graph = _build_graph
    _extract_metrics = _extract_metrics
    aggregate = aggregate
    summary = summary
    plot_metric = plot_metric
    compare_metrics = compare_metrics
    export_results = export_results
    get_graph = get_graph
    __repr__ = __repr__
