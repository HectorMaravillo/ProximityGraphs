[![CI](https://github.com/HectorMaravillo/ProximityGraphs/actions/workflows/ci.yml/badge.svg)](https://github.com/HectorMaravillo/ProximityGraphs/actions/workflows/ci.yml)
[![Docs](https://github.com/HectorMaravillo/ProximityGraphs/actions/workflows/docs.yml/badge.svg)](https://github.com/HectorMaravillo/ProximityGraphs/actions/workflows/docs.yml)
[![PyPI](https://img.shields.io/pypi/v/proximitygraphs.svg)](https://pypi.org/project/proximitygraphs/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

# ProximityGraphs

`ProximityGraphs` is a Python package for constructing, comparing, and analyzing planar proximity graphs and related geometric graph models. It provides tools to generate and transform random or structured point sets, build graphs from those points, compute graph-level metrics, and run reproducible computational experiments.

The current scope includes classical geometric and proximity graphs such as the Delaunay triangulation, Gabriel graph, Relative Neighborhood graph, Sphere-of-Influence graph, beta-skeletons, alpha shapes, convex hull graphs, nearest-neighbor graphs, and unit disk graphs. The package also includes complete graphs, Erdős--Rényi random graphs, and bio-inspired graph models.

## Installation

Install the latest release from PyPI:

```bash
pip install proximitygraphs
```

Optional GIS functionality requires the `gis` extra:

```bash
pip install "proximitygraphs[gis]"
```

## Development installation

For local development, clone the repository and install the package in editable mode:

```bash
git clone https://github.com/HectorMaravillo/ProximityGraphs.git
cd ProximityGraphs
python -m pip install -e ".[dev,docs,gis]"
```

The project uses a `src` layout. The source code lives in:

```text
src/proximitygraphs/
```

while the public import remains:

```python
import proximitygraphs as pg
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

A runnable example script is available in [`examples/quickstart.py`](examples/quickstart.py).

## API overview

The main entry points are:

* `pg.SetPoints` for generating, loading, and transforming planar point sets.
* `pg.GeometricGraph` for graph operations, analysis helpers, and visualization.
* `pg.DelaunayG`, `pg.Voronoi`, `pg.GG`, `pg.RNG`, `pg.MST`, `pg.NNG`, `pg.Unit_Disk`, `pg.SIG`, `pg.Beta_Skeleton`, `pg.Alpha_Shape`, `pg.Alpha_Hull`, and related classes for geometric and proximity graph construction.
* `pg.Experiment` for repeated simulations, metric aggregation, and reproducible graph experiments.
* `pg.PhysarumGraph` and `pg.FungalGraph` for the current bio-inspired graph models.

GIS helpers such as `SetPoints.from_geopandas()` and `GeometricGraph.to_gpd_lines()` require the optional `gis` extra.

## Documentation

The documentation is available at:

https://hectormaravillo.github.io/ProximityGraphs/

To build the documentation locally:

```bash
python -m pip install -e ".[docs]"
python -m sphinx -b html docs/source docs/build/html
```

The generated HTML documentation will be available in:

```text
docs/build/html/
```

## Testing and validation

This repository is configured and tested for:

* Windows local development
* GitHub Actions on Ubuntu
* Python 3.10, 3.11, 3.12, 3.13, and 3.14

The recommended local validation sequence is:

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
python -m ruff check .
python -m ruff format --check .
```

The test suite includes structural tests, mathematical invariant tests, seeded regression tests, and experiment-level integration tests.

## Building the package

To build the source distribution and wheel locally:

```bash
python -m pip install --upgrade build twine
python -m build
python -m twine check dist/*
```

This creates distribution files under:

```text
dist/
```

## Citation

Software citation metadata is provided in [`CITATION.cff`](CITATION.cff).

A JOSS manuscript draft is provided in [`paper/paper.md`](paper/paper.md).

The Zenodo DOI is pending until the archival release is created. After Zenodo mints the DOI, the DOI should be added to:

* `CITATION.cff`
* this `README.md`
* `paper/paper.md`

Until the archival DOI is available, cite the versioned software metadata in `CITATION.cff`.

## License

`ProximityGraphs` is distributed under the MIT License. See [`LICENSE`](LICENSE).

## Reporting issues

Bug reports and feature requests should be filed through [GitHub Issues](https://github.com/HectorMaravillo/ProximityGraphs/issues).

Security-sensitive issues should follow the instructions in [`SECURITY.md`](SECURITY.md).

## Contributing

Development setup and contribution expectations are documented in [`CONTRIBUTING.md`](CONTRIBUTING.md).
