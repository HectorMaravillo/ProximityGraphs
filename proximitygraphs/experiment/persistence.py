"""Export and retrieval helpers for ``Experiment``."""

import warnings

from ..geometricgraphs import GeometricGraph


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


def get_graph(self, simulation: int, graph_type: str) -> GeometricGraph | None:
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
            "Graphs were not stored. Run experiment with store_graphs=True.",
            stacklevel=2,
        )
        return None

    for entry in self._raw_graphs:
        if entry["simulation"] == simulation and entry["graph_type"] == graph_type:
            return entry["graph"]

    return None


def __repr__(self) -> str:
    """String representation of the experiment."""
    status = "Not run" if self.results is None else f"{len(self.results)} results"
    return (
        f"Experiment('{self.name}', simulations={self.n_simulations}, status={status})"
    )
