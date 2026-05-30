"""Experiment-level comparison with saved metrics and plots.

Run from the repository root:

    python examples/experiment_metrics.py

Outputs are written to ``examples/output/experiment_metrics``.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

import proximitygraphs as pg

OUTPUT_DIR = Path(__file__).resolve().parent / "output" / "experiment_metrics"


GRAPH_CONFIGS = [
    {"class": pg.MST, "name": "MST", "params": {}},
    {"class": pg.RNG, "name": "RNG", "params": {}},
    {"class": pg.GG, "name": "Gabriel", "params": {}},
    {
        "class": pg.Unit_Disk,
        "name": "Unit disk",
        "params": {"dist_max": 0.32},
    },
    {
        "class": pg.Gamma_Graph,
        "name": "Gamma",
        "params": {"gamma0": 0.25, "gamma1": 0.75, "block_size": 16},
    },
    {
        "class": pg.FungalGraph,
        "name": "Fungal",
        "params": {
            "steps": 2,
            "growth_iterations": 2,
            "prune_weak_factor": 0.0,
            "seed": 7,
        },
    },
]


def build_experiment():
    return pg.Experiment(
        name="Small Graph Family Comparison",
        point_config={"method": "uniform_square", "params": {"n": 18}},
        graph_configs=GRAPH_CONFIGS,
        n_simulations=4,
        seed=20260328,
        verbose=False,
    )


def save_metric_plots(experiment, output_dir=OUTPUT_DIR):
    output_dir.mkdir(parents=True, exist_ok=True)

    metric_paths = []
    for metric in ["n_edges", "total_length", "density"]:
        fig, ax = experiment.plot_metric(metric, kind="bar", figsize=(8, 4))
        ax.tick_params(axis="x", rotation=35)
        fig.tight_layout()
        path = output_dir / f"{metric}.png"
        fig.savefig(path, dpi=180, bbox_inches="tight")
        plt.close(fig)
        metric_paths.append(path)

    return metric_paths


def write_summary(experiment, output_dir=OUTPUT_DIR):
    output_dir.mkdir(parents=True, exist_ok=True)

    results_path = output_dir / "results.csv"
    aggregate_path = output_dir / "aggregate.csv"
    summary_path = output_dir / "summary.txt"

    experiment.results.to_csv(results_path, index=False)
    aggregate = experiment.aggregate(metrics=["n_edges", "total_length", "density"])
    aggregate.to_csv(aggregate_path)
    summary_path.write_text(experiment.summary() + "\n")

    return results_path, aggregate_path, summary_path


def main():
    experiment = build_experiment()
    results = experiment.run(store_graphs=True)
    results_path, aggregate_path, summary_path = write_summary(experiment)
    plot_paths = save_metric_plots(experiment)

    print(f"rows: {len(results)}")
    print(f"graph types: {', '.join(results['graph_type'].unique())}")
    print(f"saved results: {results_path.relative_to(Path.cwd())}")
    print(f"saved aggregate: {aggregate_path.relative_to(Path.cwd())}")
    print(f"saved summary: {summary_path.relative_to(Path.cwd())}")
    for path in plot_paths:
        print(f"saved plot: {path.relative_to(Path.cwd())}")


if __name__ == "__main__":
    main()
