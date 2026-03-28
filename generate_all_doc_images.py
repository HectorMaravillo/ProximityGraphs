#!/usr/bin/env python3
"""
Generate all example images referenced by the Markdown docs.

Includes:
- Points/*
- Proximity_graphs/*

Usage
-----
From the docs root (the folder that contains "Points/" and "Proximity_graphs/"):

    python generate_all_doc_images_all_fixed_v2.py

Or specify a custom docs root:

    python generate_all_doc_images_all_fixed_v2.py --docs-root /path/to/docs

Notes
-----
- This script intentionally does NOT generate the geopandas example images.
- It assumes the `proximitygraphs` package is importable (installed, or on PYTHONPATH).
- All images are saved into an `images/` folder alongside each Markdown file.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Tuple

REPO_ROOT = Path(__file__).resolve().parent
DOCS_ROOT = (REPO_ROOT / "docs" / "source" / "modules").resolve()

import numpy as np
import proximitygraphs as pg

DOC_ELEMENT_COLOR = "#4a6fa5"
DOC_BG_COLOR = "#f2f0eb"
DOC_FONT_COLOR = "#000000"


@dataclass(frozen=True)
class Job:
    name: str
    outdir: Path
    fn: Callable[[], None]


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _close_fig(fig) -> None:
    try:
        import matplotlib.pyplot as plt
        if fig is not None:
            plt.close(fig)
    except Exception:
        pass


def _unwrap_fig(ret):
    if ret is None:
        return None
    if hasattr(ret, "savefig"):
        return ret
    if isinstance(ret, tuple) and len(ret) >= 1 and hasattr(ret[0], "savefig"):
        return ret[0]
    return None


def _doc_draw_kwargs(draw_kwargs: dict, *, has_edges: bool) -> dict:
    kwargs = dict(draw_kwargs)
    kwargs.setdefault("v_color", DOC_ELEMENT_COLOR)
    if has_edges:
        kwargs.setdefault("e_color", DOC_ELEMENT_COLOR)

    fig_kwargs = dict(kwargs.get("fig_kwargs") or {})
    fig_kwargs.setdefault("facecolor", DOC_BG_COLOR)
    kwargs["fig_kwargs"] = fig_kwargs

    title_kwargs = dict(kwargs.get("title_kwargs") or {})
    title_kwargs.setdefault("color", DOC_FONT_COLOR)
    kwargs["title_kwargs"] = title_kwargs

    return kwargs


def _style_figure(fig) -> None:
    fig.patch.set_facecolor(DOC_BG_COLOR)
    for ax in fig.axes:
        ax.set_facecolor(DOC_BG_COLOR)
        ax.title.set_color(DOC_FONT_COLOR)
        ax.xaxis.label.set_color(DOC_FONT_COLOR)
        ax.yaxis.label.set_color(DOC_FONT_COLOR)
        ax.tick_params(colors=DOC_FONT_COLOR)
        for spine in ax.spines.values():
            spine.set_color(DOC_FONT_COLOR)


def _save_figure(fig, path: Path) -> None:
    _style_figure(fig)
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor=DOC_BG_COLOR)


def _save_points(pts: pg.SetPoints, outdir: Path, stem: str, *, figsize=(8, 8), **draw_kwargs) -> Path:
    _ensure_dir(outdir)
    ret = pts.draw(figsize=figsize, **_doc_draw_kwargs(draw_kwargs, has_edges=False))
    fig = _unwrap_fig(ret)
    if fig is None:
        raise RuntimeError(f"Could not obtain a matplotlib figure from {type(pts).__name__}.draw()")
    _save_figure(fig, outdir / f"{stem}.png")
    _close_fig(fig)
    return outdir / f"{stem}.png"


def _save_graph_single(graph: object, outdir: Path, stem: str, *, figsize=(8, 8), **draw_kwargs) -> Path:
    _ensure_dir(outdir)
    ret = graph.draw(figsize=figsize, **_doc_draw_kwargs(draw_kwargs, has_edges=True))
    fig = _unwrap_fig(ret)
    if fig is None:
        raise RuntimeError(f"Could not obtain a matplotlib figure from {type(graph).__name__}.draw()")
    _save_figure(fig, outdir / f"{stem}.png")
    _close_fig(fig)
    return outdir / f"{stem}.png"


def _save_graph_grid(graphs: List[object], outdir: Path, stem: str, nrows: int, ncols: int, *, figsize=(10, 10), **draw_kwargs) -> Path:
    _ensure_dir(outdir)
    doc_kwargs = _doc_draw_kwargs(draw_kwargs, has_edges=True)

    if nrows * ncols == 1:
        return _save_graph_single(graphs[0], outdir, stem, figsize=figsize, **draw_kwargs)

    # Try pg.draw_grid first
    try:
        ret = pg.draw_grid(graphs, nrows, ncols, figsize=figsize, **doc_kwargs)
        fig = _unwrap_fig(ret)
        if fig is None:
            raise RuntimeError("pg.draw_grid did not return a matplotlib figure")
        _save_figure(fig, outdir / f"{stem}.png")
        _close_fig(fig)
        return outdir / f"{stem}.png"
    except Exception:
        pass

    # Fallback: render each graph to PNG then compose
    import matplotlib.pyplot as plt
    import matplotlib.image as mpimg

    tmp_paths: List[Path] = []
    for i, g in enumerate(graphs):
        tmp_stem = f"__tmp_{stem}_{i}"
        tmp_png = outdir / f"{tmp_stem}.png"
        _save_graph_single(g, outdir, tmp_stem, figsize=figsize, **draw_kwargs)
        tmp_paths.append(tmp_png)

    fig, axes = plt.subplots(nrows, ncols, figsize=figsize, constrained_layout=True)
    axes = np.array(axes, ndmin=2)

    for ax in axes.ravel():
        ax.axis("off")

    for ax, png in zip(axes.ravel(), tmp_paths):
        img = mpimg.imread(png)
        ax.imshow(img)
        ax.axis("off")

    out_png = outdir / f"{stem}.png"
    _save_figure(fig, out_png)
    plt.close(fig)

    for png in tmp_paths:
        try:
            png.unlink()
        except Exception:
            pass

    return out_png


def _points_jobs(points_dir: Path) -> List[Job]:
    outdir = points_dir / "images"
    jobs: List[Job] = []

    jobs.append(Job("Points/uniform_square", outdir, lambda: _save_points(pg.SetPoints.uniform_square(n=200, seed=73), outdir, "uniform_square")))
    jobs.append(Job("Points/uniform_sphere", outdir, lambda: _save_points(pg.SetPoints.uniform_sphere(n=200, seed=99), outdir, "uniform_sphere")))
    jobs.append(Job("Points/uniform_over_sphere", outdir, lambda: _save_points(pg.SetPoints.uniform_over_sphere(n=200, seed=99), outdir, "uniform_over_sphere")))
    jobs.append(Job("Points/normal_dist", outdir, lambda: _save_points(pg.SetPoints.normal_dist(n=300, seed=42), outdir, "normal_dist")))
    jobs.append(Job("Points/grid", outdir, lambda: _save_points(pg.SetPoints.grid(shape=(18, 18)), outdir, "grid", v_size=18)))
    jobs.append(Job("Points/hexagonal", outdir, lambda: _save_points(pg.SetPoints.hexagonal(n_x=10, n_y=10), outdir, "hexagonal", v_size=18)))
    jobs.append(Job("Points/triangular", outdir, lambda: _save_points(pg.SetPoints.triangular(n_x=10, n_y=10), outdir, "triangular", v_size=18)))
    jobs.append(Job("Points/poissonprocess_square", outdir, lambda: _save_points(pg.SetPoints.poissonprocess_square(intensity=150, limit=1, seed=7), outdir, "poissonprocess_square")))
    jobs.append(Job("Points/poissonprocess_circle", outdir, lambda: _save_points(pg.SetPoints.poissonprocess_circle(intensity=150, radius=1, seed=7), outdir, "poissonprocess_circle")))
    jobs.append(Job("Points/poissonprocess_inhomogeneus", outdir, lambda: _save_points(pg.SetPoints.poissonprocess_inhomogeneus(fun_lambda=lambda x, y: x + y, limit=1, seed=7), outdir, "poissonprocess_inhomogeneus")))
    jobs.append(Job("Points/cluster_square", outdir, lambda: _save_points(pg.SetPoints.cluster_square(intensity=(12, 12), cluster={"name": "Matern", "param": 0.1}, limit=1, seed=7), outdir, "cluster_square")))
    jobs.append(Job("Points/draw", outdir, lambda: _save_points(pg.SetPoints.uniform_square(n=250, seed=7), outdir, "draw", v_size=10, details=True)))

    def _transformations() -> None:
        import matplotlib.pyplot as plt

        base = pg.SetPoints.uniform_square(n=300, seed=7)
        rot = base.rotation(np.pi / 6)

        try:
            scl = base.scaling(1.5)
        except TypeError:
            scl = base.scaling(scale=1.5)

        try:
            trn = base.traslation((0.4, 0.2))
        except TypeError:
            trn = base.traslation(shift=(0.4, 0.2))

        _ensure_dir(outdir)
        fig, axes = plt.subplots(2, 2, figsize=(10, 10), constrained_layout=True)
        axes = np.array(axes, ndmin=2)
        fig.patch.set_facecolor(DOC_BG_COLOR)

        for ax, (name, pts) in zip(
            axes.ravel(),
            [("base", base), ("rotation", rot), ("scaling", scl), ("translation", trn)],
        ):
            ax.set_facecolor(DOC_BG_COLOR)
            p = pts.points
            ax.scatter(p[:, 0], p[:, 1], s=10, c=DOC_ELEMENT_COLOR)
            ax.set_title(name, color=DOC_FONT_COLOR)
            ax.set_aspect("equal")
            ax.axis("off")

        _save_figure(fig, outdir / "transformations.png")
        plt.close(fig)

    jobs.append(Job("Points/transformations", outdir, _transformations))
    return jobs


def _graph_jobs(graphs_dir: Path) -> List[Job]:
    outdir = graphs_dir / "images"
    jobs: List[Job] = []

    def _delaunay() -> None:
        pts = pg.SetPoints.uniform_square(n=200, seed=42)
        _save_points(pts, outdir, "delaunay_points", figsize=(6, 6), details=True)
        G = pg.DelaunayG(pts)
        _save_graph_single(G, outdir, "delaunay", figsize=(7, 7), details=True)

    jobs.append(Job("Proximity_graphs/delaunay", outdir, _delaunay))

    def _convex_hull() -> None:
        pts = pg.SetPoints.uniform_square(n=200, seed=42)
        _save_points(pts, outdir, "convex_hull_points", figsize=(6, 6), details=True)
        G = pg.Convex_Hull(pts)
        _save_graph_single(G, outdir, "convex_hull", figsize=(7, 7), details=True)

    jobs.append(Job("Proximity_graphs/convex_hull", outdir, _convex_hull))

    def _mst() -> None:
        pts = pg.SetPoints.uniform_square(n=200, seed=42)
        _save_points(pts, outdir, "mst_points", figsize=(6, 6), details=True)
        G = pg.MST(pts)
        _save_graph_single(G, outdir, "mst", figsize=(7, 7), details=True)

    jobs.append(Job("Proximity_graphs/mst", outdir, _mst))

    def _rng() -> None:
        pts = pg.SetPoints.uniform_square(n=200, seed=42)
        _save_points(pts, outdir, "rng_points", figsize=(6, 6), details=True)
        graphs = [pg.MST(pts), pg.RNG(pts, closed=False), pg.GG(pts, closed=True)]
        _save_graph_grid(graphs, outdir, "rng", 1, 3, figsize=(15, 5), details=True)

    jobs.append(Job("Proximity_graphs/rng", outdir, _rng))

    def _gabriel_graph() -> None:
        pts = pg.SetPoints.uniform_square(n=200, seed=42)
        _save_points(pts, outdir, "gabriel_graph_points", figsize=(6, 6), details=True)
        graphs = [pg.GG(pts, closed=True), pg.GG(pts, closed=False)]
        _save_graph_grid(graphs, outdir, "gabriel_graph", 1, 2, figsize=(12, 5), details=True)

    jobs.append(Job("Proximity_graphs/gabriel_graph", outdir, _gabriel_graph))

    def _unit_disk() -> None:
        pts = pg.SetPoints.uniform_square(n=250, seed=7)
        _save_points(pts, outdir, "unit_disk_points", figsize=(6, 6), details=True)
        graphs = [
            pg.Unit_Disk(pts, dist_max=0.08, closed=True),
            pg.Unit_Disk(pts, dist_max=0.12, closed=True),
            pg.Unit_Disk(pts, dist_max=0.16, closed=True),
            pg.Unit_Disk(pts, dist_max=0.22, closed=True),
        ]
        _save_graph_grid(graphs, outdir, "unit_disk", 2, 2, figsize=(10, 10), details=True)

    jobs.append(Job("Proximity_graphs/unit_disk", outdir, _unit_disk))

    def _beta_skeleton() -> None:
        pts = pg.SetPoints.uniform_square(n=120, seed=42)
        _save_points(pts, outdir, "beta_skeleton_points", figsize=(6, 6), details=True)
        graphs = [
            pg.Beta_Skeleton(pts, beta=0.8, type_region="intersection", closed=False),
            pg.Beta_Skeleton(pts, beta=1.0, type_region="lune", closed=False),
            pg.Beta_Skeleton(pts, beta=1.5, type_region="lune", closed=False),
            pg.Beta_Skeleton(pts, beta=2.0, type_region="lune", closed=False),
            pg.Beta_Skeleton(pts, beta=2.5, type_region="lune", closed=False),
            pg.Beta_Skeleton(pts, beta=1.5, type_region="circle", closed=False),
        ]
        _save_graph_grid(graphs, outdir, "beta_skeleton", 2, 3, figsize=(15, 9), details=True)

    jobs.append(Job("Proximity_graphs/beta_skeleton", outdir, _beta_skeleton))

    def _eliptic_gg() -> None:
        pts = pg.SetPoints.uniform_square(n=150, seed=42)
        _save_points(pts, outdir, "eliptic_gg_points", figsize=(6, 6), details=True)
        graphs = [pg.Elliptic_GabrielG(pts, alpha=1.0, closed=False),
                  pg.Elliptic_GabrielG(pts, alpha=1.5, closed=False),
                  pg.Elliptic_GabrielG(pts, alpha=2.0, closed=False)]
        _save_graph_grid(graphs, outdir, "eliptic_gg", 1, 3, figsize=(15, 5), details=True)

    jobs.append(Job("Proximity_graphs/eliptic_gg", outdir, _eliptic_gg))

    def _alpha_shapes() -> None:
        theta = np.linspace(0, 2 * np.pi, 200, endpoint=False)
        r = 1 + 0.35 * np.sin(5 * theta)
        rng1 = np.random.default_rng(42)
        rng2 = np.random.default_rng(43)
        x = r * np.cos(theta) + 0.05 * rng1.standard_normal(theta.size)
        y = r * np.sin(theta) + 0.05 * rng2.standard_normal(theta.size)
        pts = pg.SetPoints(np.column_stack([x, y]))
        _save_points(pts, outdir, "alpha_shapes_points", figsize=(6, 6), details=True)
        graphs = [pg.Alpha_Shape(pts, alpha=0.1), pg.Alpha_Shape(pts, alpha=0.5),
                  pg.Alpha_Shape(pts, alpha=1.0), pg.Alpha_Shape(pts, alpha=2.0)]
        _save_graph_grid(graphs, outdir, "alpha_shapes", 2, 2, figsize=(10, 10), details=True)

    jobs.append(Job("Proximity_graphs/alpha_shapes", outdir, _alpha_shapes))

    def _alpha_hull() -> None:
        theta = np.linspace(0, 2 * np.pi, 200, endpoint=False)
        r = 1 + 0.35 * np.sin(5 * theta)
        rng1 = np.random.default_rng(42)
        rng2 = np.random.default_rng(43)
        x = r * np.cos(theta) + 0.05 * rng1.standard_normal(theta.size)
        y = r * np.sin(theta) + 0.05 * rng2.standard_normal(theta.size)
        pts = pg.SetPoints(np.column_stack([x, y]))
        _save_points(pts, outdir, "alpha_hull_points", figsize=(6, 6), details=True)
        graphs = [pg.Alpha_Hull(pts, alpha=0.5, n_points_per_arc=60),
                  pg.Alpha_Hull(pts, alpha=1.0, n_points_per_arc=60),
                  pg.Alpha_Hull(pts, alpha=-0.5, n_points_per_arc=60)]
        _save_graph_grid(graphs, outdir, "alpha_hull", 1, 3, figsize=(15, 5), details=True)

    jobs.append(Job("Proximity_graphs/alpha_hull", outdir, _alpha_hull))

    def _knn() -> None:
        pts = pg.SetPoints.uniform_square(n=250, seed=42)
        _save_points(pts, outdir, "knn_points", figsize=(6, 6), details=True)
        graphs = [pg.NNG(pts, k=3), pg.NNG(pts, k=5), pg.NNG(pts, k=10), pg.NNG(pts, k=20)]
        _save_graph_grid(graphs, outdir, "knn", 2, 2, figsize=(10, 10), details=True)

    jobs.append(Job("Proximity_graphs/knn", outdir, _knn))

    def _build_gamma() -> None:
        pts = pg.SetPoints.uniform_sphere(n=300, seed=7)
        _save_points(pts, outdir, "gamma_points", figsize=(6, 6), title=True, details=True)

        H3 = pg.Gamma_Graph(pts, gamma0=-0.5, gamma1=0.5, closed=True, block_size=128)
        H4 = pg.Gamma_Graph(pts, gamma0=-0.2, gamma1=0.5, closed=True, block_size=128)
        H5 = pg.Gamma_Graph(pts, gamma0= 0.2, gamma1=0.5, closed=True, block_size=128)
        H6 = pg.Gamma_Graph(pts, gamma0= 0.5, gamma1=0.5, closed=True, block_size=128)

        _save_graph_grid([H3, H4, H5, H6], outdir, "gamma_graph", 2, 2, figsize=(10, 10), details=True)
    
    jobs.append(Job("Proximity_graphs/gamma_graph", outdir, _build_gamma))
    
    def _build_stepping() -> None:
        pts = pg.SetPoints.uniform_square(n=300, seed=11)
        _save_points(pts, outdir, "stepping_points", figsize=(6, 6), title=True, details=True)

        G1 = pg.Stepping_Stone(pts, d=1.3, k=0, closed=True)
        G2 = pg.Stepping_Stone(pts, d=2.0, k=0, closed=False)
        G3 = pg.Stepping_Stone(pts, d=3.0, k=0, closed=True)
        G4 = pg.Stepping_Stone(pts, d=3.0, k=2, closed=True)

        _save_graph_grid([G1, G2, G3, G4], outdir, "stepping_stone", 2, 2, figsize=(10, 10), details=True)

    jobs.append(Job("Proximity_graphs/stepping_stone", outdir, _build_stepping))

    return jobs


REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_DOCS_ROOT = (REPO_ROOT / "docs" / "source" / "modules").resolve()

def main(docs_root: Path) -> int:
    points_dir = docs_root / "Points"
    graphs_dir = docs_root / "Proximity_graphs"

    if not points_dir.is_dir():
        raise FileNotFoundError(f"Expected Points/ directory under: {docs_root}")
    if not graphs_dir.is_dir():
        raise FileNotFoundError(f"Expected Proximity_graphs/ directory under: {docs_root}")
    
    jobs = _points_jobs(points_dir) + _graph_jobs(graphs_dir)

    failures: List[Tuple[str, Exception]] = []
    for job in jobs:
        try:
            job.fn()
            print(f"[OK]  {job.name}  -> {job.outdir}")
        except Exception as e:
            failures.append((job.name, e))
            print(f"[ERR] {job.name}  ({type(e).__name__}: {e})")
        finally:
            try:
                import matplotlib.pyplot as plt
                plt.close("all")
            except Exception:
                pass

    if failures:
        print("\nFailures:")
        for name, e in failures:
            print(f" - {name}: {type(e).__name__}: {e}")
        return 1

    return 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate all Markdown doc example images (incl. gamma_graph & stepping_stone)."
    )
    parser.add_argument(
        "--docs-root",
        type=str,
        default=str(DEFAULT_DOCS_ROOT),
        help="Folder that contains Points/ and Proximity_graphs/ (default: docs/source/modules/ relative to repo root).",
    )
    args = parser.parse_args()

    raise SystemExit(main(Path(args.docs_root).resolve()))
