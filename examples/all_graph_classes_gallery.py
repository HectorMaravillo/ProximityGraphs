"""Visual comparison of all public graph families.

Run from the repository root:

    python examples/all_graph_classes_gallery.py

Outputs are written to ``examples/output/all_graph_classes``.
"""

from pathlib import Path
from textwrap import wrap

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.collections import LineCollection

import proximitygraphs as pg

OUTPUT_DIR = Path(__file__).resolve().parent / "output" / "all_graph_classes"

POINTS = np.array(
    [
        [0.05, 0.08],
        [0.18, 0.42],
        [0.27, 0.18],
        [0.36, 0.78],
        [0.44, 0.38],
        [0.53, 0.12],
        [0.61, 0.66],
        [0.72, 0.30],
        [0.82, 0.86],
        [0.88, 0.48],
        [0.94, 0.14],
        [0.97, 0.74],
    ]
)


GRAPH_SPECS = [
    ("Complete", pg.GeometricGraph.complete, {}),
    ("Delaunay", pg.DelaunayG, {}),
    ("Voronoi", pg.Voronoi, {}),
    ("Convex hull", pg.Convex_Hull, {}),
    ("MST", pg.MST, {}),
    ("Unit disk", pg.Unit_Disk, {"dist_max": 0.35}),
    ("Gabriel", pg.GG, {}),
    ("RNG", pg.RNG, {}),
    ("Beta skeleton", pg.Beta_Skeleton, {"beta": 1.5, "type_region": "lune"}),
    ("Nearest neighbor", pg.NNG, {"k": 2}),
    ("Sphere influence", pg.SIG, {}),
    ("Sigma graph", pg.Sigma_Graph, {"sigma": 1.8}),
    ("Elliptic Gabriel", pg.Elliptic_GabrielG, {"alpha": 1.5}),
    ("Stepping stone", pg.Stepping_Stone, {"d": 2.0, "k": 0}),
    ("Alpha shape", pg.Alpha_Shape, {"alpha": -5}),
    ("Alpha hull", pg.Alpha_Hull, {"alpha": -5, "n_points_per_arc": 100}),
    ("Gamma graph", pg.Gamma_Graph, {"gamma0": 0.25, "gamma1": 0.75}),
    ("Physarum", pg.PhysarumGraph, {"steps": 2, "base_graph": "complete"}),
    (
        "Fungal",
        pg.FungalGraph,
        {
            "steps": 2,
            "growth_iterations": 2,
            "prune_weak_factor": 0.0,
            "seed": 20260328,
        },
    ),
]


def build_all_graphs():
    points = pg.SetPoints(POINTS.copy())
    graphs = {}
    for name, constructor, params in GRAPH_SPECS:
        graphs[name] = constructor(points, **params)
    return points, graphs


def format_params(params):
    if not params:
        return "params: defaults"
    params_text = ", ".join(f"{key}={value!r}" for key, value in params.items())
    return "\n".join(
        wrap(
            "params: " + params_text,
            width=36,
            break_long_words=False,
            break_on_hyphens=False,
        )
    )


def graph_metrics(graphs):
    rows = []
    for name, graph in graphs.items():
        max_edges = graph.n * (graph.n - 1) / 2
        total_length = float(graph.lengths.sum()) if graph.m else 0.0
        rows.append(
            {
                "graph": name,
                "vertices": graph.n,
                "edges": graph.m,
                "components": graph.cc,
                "density": round(graph.m / max_edges, 4),
                "total_length": round(total_length, 4),
                "mean_length": round(float(graph.lengths.mean()), 4)
                if graph.m
                else 0.0,
            }
        )
    return pd.DataFrame(rows)


def draw_graph_on_axis(ax, graph, color):
    if isinstance(graph, pg.Alpha_Hull):
        graph.draw(
            ax=ax,
            title=False,
            axis=True,
            v_size=18,
            v_color="#1F2933",
            e_size=1.35,
            e_color=color,
            e_alpha=0.86,
            v_kwargs={
                "edgecolors": "white",
                "linewidths": 0.45,
                "zorder": 3,
            },
        )
        style_axis(ax)
        return

    edges = graph.graph.get_edgelist()
    if edges:
        segments = np.array(
            [[graph.points[i], graph.points[j]] for i, j in edges], dtype=float
        )
        ax.add_collection(
            LineCollection(segments, linewidths=1.35, colors=color, alpha=0.86)
        )

    ax.scatter(
        graph.points[:, 0],
        graph.points[:, 1],
        s=18,
        c="#1F2933",
        edgecolors="white",
        linewidths=0.45,
        zorder=3,
    )
    style_axis(ax)


def style_axis(ax):
    ax.set_xlim(-0.03, 1.05)
    ax.set_ylim(-0.03, 1.02)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.grid(False)
    for spine in ax.spines.values():
        spine.set_color("#D7DEE8")
        spine.set_linewidth(0.8)


def save_gallery(graphs, output_dir=OUTPUT_DIR):
    output_dir.mkdir(parents=True, exist_ok=True)

    n_cols = 3
    n_rows = int(np.ceil(len(graphs) / n_cols))
    fig, axes = plt.subplots(
        n_rows,
        n_cols,
        figsize=(10.5, 16.5),
        constrained_layout=True,
    )
    axes = np.asarray(axes).ravel()
    colors = plt.cm.tab20(np.linspace(0.0, 1.0, len(graphs)))

    for ax, (name, graph), color in zip(axes, graphs.items(), colors, strict=False):
        params = next(
            spec_params
            for spec_name, _, spec_params in GRAPH_SPECS
            if spec_name == name
        )
        draw_graph_on_axis(ax, graph, color)
        ax.set_title(
            f"{name}\n{format_params(params)}\n{graph.m} edges, {graph.cc} components",
            fontsize=7.5,
            pad=5,
        )

    for ax in axes[len(graphs) :]:
        ax.set_visible(False)

    fig.suptitle("ProximityGraphs class comparison", fontsize=15)
    path = output_dir / "all_graph_classes.png"
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return path


def save_edge_count_plot(metrics, output_dir=OUTPUT_DIR):
    output_dir.mkdir(parents=True, exist_ok=True)

    sorted_metrics = metrics.sort_values("edges")
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(sorted_metrics["graph"], sorted_metrics["edges"], color="#33658A")
    ax.set_xlabel("Edges")
    ax.set_ylabel("")
    ax.set_title("Edge count by graph family")
    ax.grid(axis="x", color="#E3E8EF", linewidth=0.8)
    fig.tight_layout()

    path = output_dir / "edge_counts.png"
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return path


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
    points, graphs = build_all_graphs()
    metrics = graph_metrics(graphs)
    gallery_path = save_gallery(graphs)
    edge_count_path = save_edge_count_plot(metrics)
    csv_path, markdown_path = write_metrics(metrics)

    print(f"points: {points.n}")
    print(f"graphs: {len(graphs)}")
    print(f"saved gallery: {gallery_path.relative_to(Path.cwd())}")
    print(f"saved edge counts: {edge_count_path.relative_to(Path.cwd())}")
    print(f"saved metrics: {csv_path.relative_to(Path.cwd())}")
    print(f"saved markdown: {markdown_path.relative_to(Path.cwd())}")


if __name__ == "__main__":
    main()
