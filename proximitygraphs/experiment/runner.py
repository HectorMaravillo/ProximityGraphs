"""Execution helpers for ``Experiment``."""

import warnings
from typing import Any

import pandas as pd

from ..geometricgraphs import GeometricGraph
from ..points import SetPoints


def run(self, store_graphs: bool = False):
    """
    Execute the experiment.

    Parameters
    ----------
    store_graphs : bool, optional
        If True, store all generated graphs in memory for later access.
        Warning: This can consume significant memory for large experiments.
        Default False.

    Returns
    -------
    pd.DataFrame
        Results dataframe with columns: simulation, graph_type, and all metrics.
    """
    if not self.point_config or not self.graph_configs:
        raise ValueError(
            "Both point_config and graph_configs must be set before running."
        )

    results_list = []

    if self.verbose:
        print(f"Running experiment: {self.name}")
        print(f"Simulations: {self.n_simulations}")
        print(f"Graph types: {len(self.graph_configs)}")
        print("-" * 50)

    for sim in range(self.n_simulations):
        if self.verbose and (sim + 1) % max(1, self.n_simulations // 10) == 0:
            print(f"Progress: {sim + 1}/{self.n_simulations} simulations")

        # Generate seed for this simulation
        sim_seed = self._rng.integers(0, 2**31) if self.seed is not None else None

        # Generate points
        try:
            points = self._generate_points(sim_seed)
        except Exception as e:
            warnings.warn(
                f"Failed to generate points in simulation {sim}: {e}", stacklevel=2
            )
            continue

        # Build graphs for this point set
        for graph_config in self.graph_configs:
            try:
                graph = self._build_graph(points, graph_config)
                metrics = self._extract_metrics(graph, sim, graph_config["name"])
                results_list.append(metrics)

                if store_graphs:
                    self._raw_graphs.append(
                        {
                            "simulation": sim,
                            "graph_type": graph_config["name"],
                            "graph": graph,
                            "points": points,
                        }
                    )

            except Exception as e:
                msg = f"Failed to build {graph_config['name']} in simulation {sim}: {e}"
                warnings.warn(
                    msg,
                    stacklevel=2,
                )
                continue

    if not results_list:
        raise RuntimeError("No valid results were generated.")

    # Create results DataFrame
    self.results = pd.DataFrame(results_list)

    if self.verbose:
        print("-" * 50)
        print(f"Experiment complete. {len(self.results)} results collected.")

    return self.results


def _generate_points(self, seed: int | None) -> SetPoints:
    """Generate a point set according to configuration and apply transformations."""
    method_name = self.point_config["method"]
    params = self.point_config["params"].copy()

    # Add seed to params
    if seed is not None:
        params["seed"] = seed

    # Get the method from SetPoints class
    if not hasattr(SetPoints, method_name):
        raise AttributeError(f"SetPoints has no method '{method_name}'")

    method = getattr(SetPoints, method_name)
    points = method(**params)

    # Apply transformations if any
    transformations = self.point_config.get("transformations", [])
    for transform in transformations:
        transform_method = transform.get("method")
        transform_params = transform.get("params", {})

        if not transform_method:
            warnings.warn(
                "Transformation missing 'method' key, skipping.", stacklevel=2
            )
            continue

        # Check if the transformation method exists
        if not hasattr(points, transform_method):
            msg = (
                f"SetPoints has no transformation method "
                f"'{transform_method}', skipping."
            )
            warnings.warn(
                msg,
                stacklevel=2,
            )
            continue

        # Apply the transformation
        try:
            transform_func = getattr(points, transform_method)
            points = transform_func(**transform_params)
        except Exception as e:
            warnings.warn(
                f"Failed to apply transformation '{transform_method}': {e}",
                stacklevel=2,
            )
            continue

    return points


def _build_graph(self, points: SetPoints, config: dict[str, Any]) -> GeometricGraph:
    """Build a graph according to configuration."""
    graph_class = config["class"]
    params = config["params"].copy()

    # Instantiate graph
    return graph_class(points, **params)
