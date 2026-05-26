[![CI](https://github.com/HectorMaravillo/proximitygraphs/actions/workflows/ci.yml/badge.svg)](https://github.com/HectorMaravillo/proximitygraphs/actions/workflows/ci.yml)
[![Docs](https://github.com/HectorMaravillo/proximitygraphs/actions/workflows/docs.yml/badge.svg)](https://github.com/HectorMaravillo/proximitygraphs/actions/workflows/docs.yml)

# ProximityGraphs

ProximityGraphs is a Python-based computational geometry package for constructing and analyzing proximity and biological graphs, facilitating computational experimentation. It provides tools to generate and transform random and structured point sets and to build graphs from them. Its current scope comprises  13 geometric graphs, most of them proximity graphs—such as the Delaunay triangulation, the Gabriel graph, the Relative Neighborhood graph, and the Sphere-of-Influence graph—as well as the complete graph, the Erdős-Rényi random graph and two bio-inspired graphs.


## Installation

We are on pipi! https://pypi.org/project/proximitygraphs/

```bash
pip install proximitygraphs
```


Or the editable on github

```bash
python -m pip install -e ".[dev, docs, gis]"
```

and to update the page
```bash
python -m sphinx -b html docs/source docs/build/html
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
- Python 3.10, 3.11, 3.12, 3.13 and 3.14

The recommended validation sequence is:

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
python -m ruff check .
python -m ruff format --check .
```

## Citation

Software citation metadata is provided in [CITATION.cff](CITATION.cff). A JOSS-ready manuscript draft is provided in [paper.md](paper/paper.md).

The Zenodo DOI is still pending. Until archival metadata is finalized, use the versioned software citation in `CITATION.cff` and update it after a DOI is minted.

## License

ProximityGraphs is distributed under the MIT License. See [LICENSE](LICENSE).

## Reporting Issues

Bug reports and feature requests should be filed through [GitHub Issues](https://github.com/HectorMaravillo/proximitygraphs/issues). Security-sensitive issues should follow [SECURITY.md](SECURITY.md).

## Contributing

Development setup and contribution expectations are documented in [CONTRIBUTING.md](CONTRIBUTING.md).
