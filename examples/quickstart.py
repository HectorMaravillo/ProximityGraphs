"""Quickstart example for deterministic proximity graph construction.

Run from the repository root:

    python examples/quickstart.py

The script prints a compact summary and writes a comparison figure plus metrics
table under ``examples/output/quickstart``.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

import proximitygraphs as pg

OUTPUT_DIR = Path(__file__).resolve().parent / "output" / "quickstart"


def build_graphs():
    points = pg.SetPoints.grid(shape=(3, 3))
    graphs = {
        "MST": pg.MST(points),
        "Unit disk": pg.Unit_Disk(points, dist_max=1.01),
        "Gabriel": pg.GG(points),
        "Relative neighborhood": pg.RNG(points),
        "Delaunay": pg.DelaunayG(points),
        "Voronoi": pg.Voronoi(points),
    }
    return points, graphs


def graph_metrics(graphs):
    rows = []
    for name, graph in graphs.items():
        total_length = float(graph.lengths.sum()) if graph.m else 0.0
        rows.append(
            {
                "graph": name,
                "vertices": graph.n,
                "edges": graph.m,
                "components": graph.cc,
                "density": round(graph.m / (graph.n * (graph.n - 1) / 2), 4),
                "total_length": round(total_length, 4),
            }
        )
    return pd.DataFrame(rows)


def save_graph_gallery(graphs, output_dir=OUTPUT_DIR):
    output_dir.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(1, len(graphs), figsize=(16, 3), constrained_layout=True)
    colors = ["#2F4858", "#33658A", "#F6AE2D", "#F26419", "#5B8E7D", "#8E5572"]
    for ax, (name, graph), color in zip(axes, graphs.items(), colors, strict=True):
        graph.draw(
            ax=ax,
            title=False,
            axis=True,
            v_size=28,
            v_color="#1B1B1E",
            e_size=2,
            e_color=color,
            e_alpha=0.9,
        )
        ax.set_title(name, fontsize=10)
        ax.set_xticks([])
        ax.set_yticks([])

    figure_path = output_dir / "graph_gallery.png"
    fig.savefig(figure_path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return figure_path


def write_metrics(metrics, output_dir=OUTPUT_DIR):
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "metrics.csv"
    markdown_path = output_dir / "metrics.md"

    metrics.to_csv(csv_path, index=False)
    header = "| " + " | ".join(metrics.columns) + " |"
    divider = "| " + " | ".join(["---"] * len(metrics.columns)) + " |"
    rows = [
        "| " + " | ".join(str(value) for value in row) + " |"
        for row in metrics.itertuples(index=False, name=None)
    ]
    markdown_path.write_text("\n".join([header, divider, *rows]) + "\n")
    return csv_path, markdown_path


def main():
    points, graphs = build_graphs()
    metrics = graph_metrics(graphs)
    figure_path = save_graph_gallery(graphs)
    csv_path, markdown_path = write_metrics(metrics)

    print(f"points: {points.n}")
    print(f"graphs: {', '.join(graphs)}")
    print(f"mst edges: {graphs['MST'].m}")
    print(f"unit disk edges: {graphs['Unit disk'].m}")
    print(f"saved figure: {figure_path.relative_to(Path.cwd())}")
    print(f"saved metrics: {csv_path.relative_to(Path.cwd())}")
    print(f"saved markdown: {markdown_path.relative_to(Path.cwd())}")


if __name__ == "__main__":
    main()
