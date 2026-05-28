# Contributing

## Development Setup

Clone the repository and install the package in editable mode with development tooling:

```bash
python -m pip install -e ".[dev]"
```

The project uses a `src` layout: source code lives in `src/proximitygraphs/`,
while the public import remains `import proximitygraphs as pg`.

If you need GeoPandas/Shapely integrations:

```bash
python -m pip install -e ".[gis]"
```

If you want to build the Sphinx documentation locally:

```bash
python -m pip install -e ".[docs,gis]"
```

## Running Checks

Run the test suite:

```bash
python -m pytest -q
```

Run lint checks:

```bash
python -m ruff check .
python -m ruff format --check .
```

Build the documentation:

```bash
python -m sphinx -b html docs/source docs/build/html
```

## Releasing

Versions are derived from Git tags via setuptools-scm.

To release version 0.1.0:

```bash
git checkout main
git pull
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0
```

The publish workflow runs on tags matching `v*`. Do not edit `__version__`
manually.

## Style Rules

- Keep changes focused and well-scoped.
- Prefer ASCII in source files unless non-ASCII is required for names or citations.
- Preserve public class names and package import paths unless a breaking change is explicitly intended.
- Add or update tests for behavior changes.
- Keep documentation examples runnable against the current package API.

## Pull Requests

- Work from a feature branch.
- Make sure local tests and Ruff checks pass before opening a pull request.
- Summarize user-visible changes and any follow-up work in the pull request description.
- Link related issues when applicable.
