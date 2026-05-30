"""Covers small smoke tests for examples and a few stable graph behaviors."""

import importlib.util
import json
from pathlib import Path

import numpy as np

import proximitygraphs as pg


def load_quickstart_module():
    quickstart_path = Path(__file__).resolve().parents[1] / "examples" / "quickstart.py"
    spec = importlib.util.spec_from_file_location("quickstart", quickstart_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_experiment_metrics_module():
    example_path = (
        Path(__file__).resolve().parents[1] / "examples" / "experiment_metrics.py"
    )
    spec = importlib.util.spec_from_file_location("experiment_metrics", example_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_all_graph_classes_module():
    example_path = (
        Path(__file__).resolve().parents[1]
        / "examples"
        / "all_graph_classes_gallery.py"
    )
    spec = importlib.util.spec_from_file_location(
        "all_graph_classes_gallery", example_path
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_uniform_square_is_reproducible_with_seed():
    points_a = pg.SetPoints.uniform_square(n=5, seed=123)
    points_b = pg.SetPoints.uniform_square(n=5, seed=123)

    assert points_a.n == 5
    assert points_a.dim == 2
    assert np.allclose(points_a.points, points_b.points)


def test_mst_on_2x2_grid_has_tree_structure_and_unit_lengths():
    points = pg.SetPoints.grid(shape=(2, 2))
    graph = pg.MST(points)

    assert graph.n == 4
    assert graph.m == graph.n - 1
    assert graph.graph.is_tree()
    assert np.allclose(np.sort(graph.lengths), np.ones(3))


def test_gamma_graph_special_cases_match_documented_extremes():
    points = pg.SetPoints.grid(shape=(2, 2))

    void_graph = pg.Gamma_Graph(points, gamma0=1.0, gamma1=1.0)
    complete_graph = pg.Gamma_Graph(points, gamma0=-1.0, gamma1=-1.0)

    assert void_graph.m == 0
    assert complete_graph.m == 6
    assert sorted(complete_graph.graph.get_edgelist()) == [
        (0, 1),
        (0, 2),
        (0, 3),
        (1, 2),
        (1, 3),
        (2, 3),
    ]


def test_quickstart_main_prints_expected_summary(capsys):
    quickstart = load_quickstart_module()

    quickstart.main()
    captured = capsys.readouterr()

    assert captured.out.splitlines() == [
        "points: 9",
        "graphs: MST, Unit disk, Gabriel, Relative neighborhood, Delaunay, Voronoi",
        "mst edges: 8",
        "unit disk edges: 12",
        r"saved figure: examples\output\quickstart\graph_gallery.png",
        r"saved metrics: examples\output\quickstart\metrics.csv",
        r"saved markdown: examples\output\quickstart\metrics.md",
    ]


def test_quickstart_writes_gallery_and_metrics_to_requested_directory(tmp_path):
    quickstart = load_quickstart_module()

    _points, graphs = quickstart.build_graphs()
    metrics = quickstart.graph_metrics(graphs)
    figure_path = quickstart.save_graph_gallery(graphs, tmp_path)
    csv_path, markdown_path = quickstart.write_metrics(metrics, tmp_path)

    assert figure_path.exists()
    assert figure_path.stat().st_size > 0
    assert csv_path.read_text().splitlines()[0] == (
        "graph,vertices,edges,components,density,total_length"
    )
    assert "Relative neighborhood" in markdown_path.read_text()


def test_experiment_metrics_example_writes_results_and_plots(tmp_path):
    example = load_experiment_metrics_module()
    experiment = example.build_experiment()
    results = experiment.run(store_graphs=True)

    results_path, aggregate_path, summary_path = example.write_summary(
        experiment, tmp_path
    )
    plot_paths = example.save_metric_plots(experiment, tmp_path)

    assert len(results) == 24
    assert set(results["graph_type"]) == {
        "MST",
        "RNG",
        "Gabriel",
        "Unit disk",
        "Gamma",
        "Fungal",
    }
    assert results_path.exists()
    assert aggregate_path.exists()
    assert "Small Graph Family Comparison" in summary_path.read_text()
    assert len(plot_paths) == 3
    assert all(path.exists() and path.stat().st_size > 0 for path in plot_paths)


def test_all_graph_classes_gallery_writes_visual_comparison_and_metrics(tmp_path):
    example = load_all_graph_classes_module()
    points, graphs = example.build_all_graphs()
    metrics = example.graph_metrics(graphs)

    gallery_path = example.save_gallery(graphs, tmp_path)
    edge_count_path = example.save_edge_count_plot(metrics, tmp_path)
    csv_path, markdown_path = example.write_metrics(metrics, tmp_path)

    assert points.n == 12
    assert len(graphs) == 19
    assert {"Physarum", "Fungal", "Gamma graph", "Alpha hull", "Voronoi"} <= set(graphs)
    assert list(metrics.columns) == [
        "graph",
        "vertices",
        "edges",
        "components",
        "density",
        "total_length",
        "mean_length",
    ]
    assert gallery_path.exists()
    assert gallery_path.stat().st_size > 0
    assert edge_count_path.exists()
    assert edge_count_path.stat().st_size > 0
    assert csv_path.exists()
    assert "Fungal" in markdown_path.read_text()


def test_gallery_notebook_has_runnable_cells_and_markdown_explanations():
    notebook_path = Path(__file__).resolve().parents[1] / "examples"
    notebook_path = notebook_path / "proximitygraphs_gallery.ipynb"
    notebook = json.loads(notebook_path.read_text())
    cells = notebook["cells"]

    markdown_text = "\n".join(
        "".join(cell["source"]) for cell in cells if cell["cell_type"] == "markdown"
    )
    code_text = "\n".join(
        "".join(cell["source"]) for cell in cells if cell["cell_type"] == "code"
    )

    assert notebook["nbformat"] == 4
    assert "ProximityGraphs Gallery and Metrics" in markdown_text
    assert "Experiment-Level Comparison" in markdown_text
    assert "quickstart.build_graphs" in code_text
    assert "experiment_metrics.build_experiment" in code_text


def test_quickstart_notebook_has_gallery_and_metrics_sections():
    notebook_path = Path(__file__).resolve().parents[1] / "examples"
    notebook_path = notebook_path / "quickstart.ipynb"
    notebook = json.loads(notebook_path.read_text())
    cells = notebook["cells"]

    markdown_text = "\n".join(
        "".join(cell["source"]) for cell in cells if cell["cell_type"] == "markdown"
    )
    code_text = "\n".join(
        "".join(cell["source"]) for cell in cells if cell["cell_type"] == "code"
    )

    assert notebook["nbformat"] == 4
    assert "Quickstart: Build and Compare" in markdown_text
    assert "Visual Comparison" in markdown_text
    assert "Metrics" in markdown_text
    assert "quickstart.build_graphs" in code_text
    assert "quickstart.save_graph_gallery" in code_text


def test_all_graph_classes_notebook_has_visual_comparison_sections():
    notebook_path = Path(__file__).resolve().parents[1] / "examples"
    notebook_path = notebook_path / "all_graph_classes_gallery.ipynb"
    notebook = json.loads(notebook_path.read_text())
    cells = notebook["cells"]

    markdown_text = "\n".join(
        "".join(cell["source"]) for cell in cells if cell["cell_type"] == "markdown"
    )
    code_text = "\n".join(
        "".join(cell["source"]) for cell in cells if cell["cell_type"] == "code"
    )

    assert notebook["nbformat"] == 4
    assert "All Graph Classes Visual Comparison" in markdown_text
    assert "PhysarumGraph" in markdown_text
    assert "FungalGraph" in markdown_text
    assert "gallery.build_all_graphs" in code_text
    assert "gallery.save_gallery" in code_text
