import numpy as np
import pandas as pd
from typing import Dict, List, Callable, Any, Optional, Tuple
import warnings
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes

from .points import SetPoints
from .geometricgraphs import GeometricGraph


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
        point_config: Optional[Dict[str, Any]] = None,
        graph_configs: Optional[List[Dict[str, Any]]] = None,
        n_simulations: int = 30,
        seed: Optional[int] = None,
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
            Master random seed for reproducibility. If None, results are non-deterministic.
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
        self.results: Optional[pd.DataFrame] = None
        self.aggregated: Optional[pd.DataFrame] = None
        self._raw_graphs: List[Dict[str, Any]] = []

        # Custom metrics registry
        self._custom_metrics: Dict[str, Callable] = {}

        # Validation
        self._validate_config()

        # Initialize random state
        if seed is not None:
            self._rng = np.random.default_rng(seed)
        else:
            self._rng = np.random.default_rng()

    def _validate_config(self):
        """Validate experiment configuration."""
        if not self.point_config:
            warnings.warn("No point configuration provided. Use add_point_config().")

        if not self.graph_configs:
            warnings.warn("No graph configurations provided. Use add_graph_config().")

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
        transformations: Optional[List[Dict[str, Any]]] = None,
        **params,
    ):
        """
        Add or update point generation configuration.

        Parameters
        ----------
        method : str
            Name of SetPoints class method (e.g., 'uniform_square', 'normal_dist').
        transformations : list of dict, optional
            List of transformations to apply after point generation. Each dict must contain:
            - 'method': str, name of transformation method ('rotation', 'scaling', 'traslation', 'perturb')
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

    def add_graph_config(self, graph_class, name: Optional[str] = None, **params):
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
                warnings.warn(f"Failed to generate points in simulation {sim}: {e}")
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
                    warnings.warn(
                        f"Failed to build {graph_config['name']} in simulation {sim}: {e}"
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

    def _generate_points(self, seed: Optional[int]) -> SetPoints:
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
                warnings.warn("Transformation missing 'method' key, skipping.")
                continue

            # Check if the transformation method exists
            if not hasattr(points, transform_method):
                warnings.warn(
                    f"SetPoints has no transformation method '{transform_method}', skipping."
                )
                continue

            # Apply the transformation
            try:
                transform_func = getattr(points, transform_method)
                points = transform_func(**transform_params)
            except Exception as e:
                warnings.warn(
                    f"Failed to apply transformation '{transform_method}': {e}"
                )
                continue

        return points

    def _build_graph(self, points: SetPoints, config: Dict[str, Any]) -> GeometricGraph:
        """Build a graph according to configuration."""
        graph_class = config["class"]
        params = config["params"].copy()

        # Instantiate graph
        return graph_class(points, **params)

    def _extract_metrics(
        self, graph: GeometricGraph, simulation: int, graph_type: str
    ) -> Dict[str, Any]:
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
        except:
            metrics["entropy_degree"] = 0.0

        try:
            metrics["entropy_length"] = graph.entropy("length", bins=10)
        except:
            metrics["entropy_length"] = 0.0

        try:
            metrics["entropy_orientation"] = graph.entropy("orientation", bins=36)
        except:
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
                warnings.warn(f"Custom metric '{metric_name}' failed: {e}")
                metrics[metric_name] = np.nan

        return metrics

    def aggregate(
        self, groupby: str = "graph_type", metrics: Optional[List[str]] = None
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

    def plot_metric(
        self,
        metric: str,
        kind: str = "bar",
        figsize: Tuple[int, int] = (10, 6),
        title: Optional[str] = None,
        **kwargs,
    ) -> Tuple[Figure, Axes]:
        """
        Plot a specific metric across graph types.

        Parameters
        ----------
        metric : str
            Name of the metric to plot (must be in results columns).
        kind : str, optional
            Type of plot: 'bar', 'box', 'violin', 'line'. Default 'bar'.
        figsize : tuple, optional
            Figure size. Default (10, 6).
        title : str, optional
            Plot title. If None, generates automatic title.
        **kwargs
            Additional arguments passed to plotting function.

        Returns
        -------
        fig, ax : matplotlib Figure and Axes
        """
        if self.results is None:
            raise RuntimeError("No results available. Run experiment first.")

        if metric not in self.results.columns:
            raise ValueError(f"Metric '{metric}' not found in results.")

        fig, ax = plt.subplots(figsize=figsize)

        if kind == "bar":
            # Bar plot with error bars
            if self.aggregated is None:
                self.aggregate()

            means = self.aggregated[metric]["mean"]
            stds = self.aggregated[metric]["std"]

            means.plot(kind="bar", yerr=stds, ax=ax, capsize=5, **kwargs)
            ax.set_ylabel(metric.replace("_", " ").title())
            ax.set_xlabel("Graph Type")

        elif kind == "box":
            # Box plot
            self.results.boxplot(column=metric, by="graph_type", ax=ax, **kwargs)
            ax.set_ylabel(metric.replace("_", " ").title())
            ax.set_xlabel("Graph Type")
            plt.suptitle("")  # Remove automatic title

        elif kind == "violin":
            # Violin plot (requires seaborn)
            try:
                import seaborn as sns

                sns.violinplot(
                    data=self.results, x="graph_type", y=metric, ax=ax, **kwargs
                )
                ax.set_ylabel(metric.replace("_", " ").title())
                ax.set_xlabel("Graph Type")
            except ImportError:
                raise ImportError(
                    "Seaborn required for violin plots. Install with: pip install seaborn"
                )

        elif kind == "line":
            # Line plot (useful for showing trends across simulations)
            for graph_type in self.results["graph_type"].unique():
                subset = self.results[self.results["graph_type"] == graph_type]
                ax.plot(
                    subset["simulation"], subset[metric], label=graph_type, **kwargs
                )
            ax.set_xlabel("Simulation")
            ax.set_ylabel(metric.replace("_", " ").title())
            ax.legend()

        else:
            raise ValueError(f"Unknown plot kind: {kind}")

        if title is None:
            title = f"{metric.replace('_', ' ').title()} - {self.name}"
        ax.set_title(title)

        plt.tight_layout()
        return fig, ax

    def compare_metrics(
        self, metrics: List[str], figsize: Tuple[int, int] = (14, 10), **kwargs
    ) -> Tuple[Figure, np.ndarray]:
        """
        Create a grid of plots comparing multiple metrics.

        Parameters
        ----------
        metrics : list of str
            List of metric names to plot.
        figsize : tuple, optional
            Figure size. Default (14, 10).
        **kwargs
            Additional arguments passed to individual plot functions.

        Returns
        -------
        fig, axes : matplotlib Figure and array of Axes
        """
        if self.results is None:
            raise RuntimeError("No results available. Run experiment first.")

        n_metrics = len(metrics)
        n_cols = 2
        n_rows = (n_metrics + n_cols - 1) // n_cols

        fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
        axes = np.atleast_2d(axes).flatten()

        for idx, metric in enumerate(metrics):
            if metric not in self.results.columns:
                warnings.warn(f"Metric '{metric}' not found, skipping.")
                continue

            ax = axes[idx]

            # Box plot for each metric
            self.results.boxplot(column=metric, by="graph_type", ax=ax, **kwargs)
            ax.set_title(metric.replace("_", " ").title())
            ax.set_xlabel("")
            plt.suptitle("")

        # Hide unused subplots
        for idx in range(n_metrics, len(axes)):
            axes[idx].set_visible(False)

        fig.suptitle(f"Metric Comparison - {self.name}", fontsize=14, y=0.995)
        plt.tight_layout()

        return fig, axes

    def export_results(self, filepath: str, format: str = "csv"):
        """
        Export results to file.

        Parameters
        ----------
        filepath : str
            Output file path.
        format : str, optional
            Output format: 'csv', 'excel', 'json', 'pickle'. Default 'csv'.
        """
        if self.results is None:
            raise RuntimeError("No results available. Run experiment first.")

        if format == "csv":
            self.results.to_csv(filepath, index=False)
        elif format == "excel":
            self.results.to_excel(filepath, index=False)
        elif format == "json":
            self.results.to_json(filepath, orient="records", indent=2)
        elif format == "pickle":
            self.results.to_pickle(filepath)
        else:
            raise ValueError(f"Unknown format: {format}")

        if self.verbose:
            print(f"Results exported to {filepath}")

    def get_graph(self, simulation: int, graph_type: str) -> Optional[GeometricGraph]:
        """
        Retrieve a specific graph from stored results.

        Parameters
        ----------
        simulation : int
            Simulation number.
        graph_type : str
            Graph type name.

        Returns
        -------
        GeometricGraph or None
            The requested graph, or None if not found or not stored.
        """
        if not self._raw_graphs:
            warnings.warn(
                "Graphs were not stored. Run experiment with store_graphs=True."
            )
            return None

        for entry in self._raw_graphs:
            if entry["simulation"] == simulation and entry["graph_type"] == graph_type:
                return entry["graph"]

        return None

    def __repr__(self) -> str:
        """String representation of the experiment."""
        status = "Not run" if self.results is None else f"{len(self.results)} results"
        return f"Experiment('{self.name}', simulations={self.n_simulations}, status={status})"
