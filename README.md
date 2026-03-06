[![CI](https://github.com/HectorMaravillo/proximitygraphs/actions/workflows/ci.yml/badge.svg)](https://github.com/HectorMaravillo/proximitygraphs/actions/workflows/ci.yml)
[![Docs](https://github.com/HectorMaravillo/proximitygraphs/actions/workflows/docs.yml/badge.svg)](https://github.com/HectorMaravillo/proximitygraphs/actions/workflows/docs.yml)

# ProximityGraphs

ProximityGraphs is a Python library for generating planar point sets, building proximity graphs on top of them, and comparing graph families under a shared interface. The package combines geometric graph constructors such as Delaunay triangulations, Gabriel graphs, relative neighborhood graphs, minimum spanning trees, unit disk graphs, alpha shapes, and gamma graphs with a small experiment framework and bio-inspired graph models.

The project is aimed at teaching, exploratory computational geometry, and reproducible experiments on planar point patterns. It builds on NumPy, SciPy, igraph, matplotlib, and pandas while keeping GIS exports optional.

## Installation

Install the core package in editable mode:

```bash
python -m pip install -e .
```

Install development tools:

```bash
python -m pip install -e ".[dev]"
```

Install optional GIS support for GeoPandas/Shapely-based helpers:

```bash
python -m pip install -e ".[gis]"
```

Install documentation dependencies:

```bash
python -m pip install -e ".[docs,gis]"
```

## Quickstart

```python
import proximitygraphs as pg

points = pg.SetPoints.grid(shape=(3, 3))
mst = pg.MST(points)
unit_disk = pg.Unit_Disk(points, dist_max=1.01)

print(points.n)                   # 9 vertices
print(mst.m)                      # 8 edges
print(unit_disk.graph.get_edgelist())
```

A runnable example script is available at [examples/quickstart.py](examples/quickstart.py).

## API Overview

The main entry points are:

- `pg.SetPoints` for generating or loading planar point sets.
- `pg.GeometricGraph` for graph operations, analysis helpers, and visualization.
- `pg.DelaunayG`, `pg.GG`, `pg.RNG`, `pg.MST`, `pg.Unit_Disk`, `pg.Alpha_Shape`, and related classes for proximity graph construction.
- `pg.Experiment` for repeated simulations and metric aggregation.
- `pg.PhysarumGraph` for the package's current bio-inspired graph model.

GIS helpers such as `SetPoints.from_geopandas()` and `GeometricGraph.to_gpd_lines()` require the optional `gis` extra.

## Reproducibility / Installation

This repository is configured and tested for:

- Windows local development
- GitHub Actions on Ubuntu
- Python 3.10, 3.11, and 3.12

The recommended validation sequence is:

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
python -m ruff check .
python -m ruff format --check .
```

## Citation

Software citation metadata is provided in [CITATION.cff](CITATION.cff). A JOSS-ready manuscript draft is provided in [paper.md](paper.md).

The Zenodo DOI is still pending. Until archival metadata is finalized, use the versioned software citation in `CITATION.cff` and update it after a DOI is minted.

## License

ProximityGraphs is distributed under the MIT License. See [LICENSE](LICENSE).

## Reporting Issues

Bug reports and feature requests should be filed through [GitHub Issues](https://github.com/HectorMaravillo/proximitygraphs/issues). Security-sensitive issues should follow [SECURITY.md](SECURITY.md).

## Contributing

Development setup and contribution expectations are documented in [CONTRIBUTING.md](CONTRIBUTING.md).
