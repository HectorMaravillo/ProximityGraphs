"""Plotting helpers for ``Experiment``."""

import warnings

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure


def plot_metric(
    self,
    metric: str,
    kind: str = "bar",
    figsize: tuple[int, int] = (10, 6),
    title: str | None = None,
    **kwargs,
) -> tuple[Figure, Axes]:
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

            sns.violinplot(data=self.results, x="graph_type", y=metric, ax=ax, **kwargs)
            ax.set_ylabel(metric.replace("_", " ").title())
            ax.set_xlabel("Graph Type")
        except ImportError as exc:
            raise ImportError(
                "Seaborn required for violin plots. Install with: pip install seaborn"
            ) from exc

    elif kind == "line":
        # Line plot (useful for showing trends across simulations)
        for graph_type in self.results["graph_type"].unique():
            subset = self.results[self.results["graph_type"] == graph_type]
            ax.plot(subset["simulation"], subset[metric], label=graph_type, **kwargs)
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
    self, metrics: list[str], figsize: tuple[int, int] = (14, 10), **kwargs
) -> tuple[Figure, np.ndarray]:
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
            warnings.warn(f"Metric '{metric}' not found, skipping.", stacklevel=2)
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
