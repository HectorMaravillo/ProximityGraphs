# ProximityGraphs Examples

This folder contains small, deterministic examples that generate both figures
and metrics. Run them from the repository root so relative output paths are
stable.

## Quickstart Gallery

```bash
python examples/quickstart.py
```

Builds a 3x3 grid and compares five graph families:

- minimum spanning tree
- unit disk graph
- Gabriel graph
- relative neighborhood graph
- Delaunay triangulation

Outputs:

- `examples/output/quickstart/graph_gallery.png`
- `examples/output/quickstart/metrics.csv`
- `examples/output/quickstart/metrics.md`

Notebook version:

```text
examples/quickstart.ipynb
```

It walks through the same small grid example with markdown explanations, an
inline gallery, and a metrics table.

## Experiment Metrics

```bash
python examples/experiment_metrics.py
```

Uses the high-level `Experiment` API to run four seeded simulations over a
shared random point-set workflow and compare graph families with saved metrics.

Outputs:

- `examples/output/experiment_metrics/results.csv`
- `examples/output/experiment_metrics/aggregate.csv`
- `examples/output/experiment_metrics/summary.txt`
- `examples/output/experiment_metrics/n_edges.png`
- `examples/output/experiment_metrics/total_length.png`
- `examples/output/experiment_metrics/density.png`

## All Graph Classes Gallery

```bash
python examples/all_graph_classes_gallery.py
```

Builds every public graph family on the same deterministic point set, including
the bio-inspired `PhysarumGraph` and `FungalGraph`, and renders a direct visual
comparison.

Outputs:

- `examples/output/all_graph_classes/all_graph_classes.png`
- `examples/output/all_graph_classes/edge_counts.png`
- `examples/output/all_graph_classes/metrics.csv`
- `examples/output/all_graph_classes/metrics.md`

Notebook version:

```text
examples/all_graph_classes_gallery.ipynb
```

It includes markdown explanations, the full visual gallery, a sorted metrics
table, and the edge-count comparison plot.

## Notebook Gallery

Open:

```text
examples/proximitygraphs_gallery.ipynb
```

The notebook walks through the same ideas with markdown explanations, inline
tables, and displayed PNG outputs. It writes artifacts to
`examples/output/notebook/`.

The examples use Matplotlib's non-interactive backend, so they are safe to run
in terminals, notebooks, and CI jobs.
