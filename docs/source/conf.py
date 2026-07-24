# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import json
import shutil
from pathlib import Path

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Proximity Graphs"
copyright = "2025, Héctor Maravillo"
author = "Héctor Maravillo , Diego Villarreal , Heriberto Espino"
release = "v0.1.0a1"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_nb",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.mathjax",
    "sphinx_autodoc_typehints",
    "sphinxcontrib.bibtex",
]

bibtex_bibfiles = ["biblio.bib"]

myst_enable_extensions = [
    "deflist",
    "colon_fence",
    "dollarmath",
    "amsmath",
    "html_image",
]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "myst-nb",
    ".ipynb": "myst-nb",
}

templates_path = ["_templates"]
exclude_patterns = []
nb_execution_mode = "off"
suppress_warnings = ["mystnb.unknown_mime_type"]


def _sync_example_notebooks(app):
    """Copy the canonical example notebooks into Sphinx's source tree."""
    docs_source = Path(__file__).resolve().parent
    repository_root = docs_source.parents[1]
    notebook_source = repository_root / "examples_notebooks"
    notebook_target = docs_source / "examples_notebooks"

    if not notebook_source.is_dir():
        raise FileNotFoundError(
            f"Example notebook directory does not exist: {notebook_source}"
        )

    if notebook_target.exists():
        shutil.rmtree(notebook_target)

    shutil.copytree(
        notebook_source,
        notebook_target,
        ignore=shutil.ignore_patterns(".ipynb_checkpoints", "__pycache__"),
    )

    notebooks = sorted(notebook_target.rglob("*.ipynb"))
    toctree = [
        "Example notebooks",
        "=================",
        "",
        "These notebooks are rendered from ``examples_notebooks`` without being",
        "executed during the documentation build.",
        "",
        ".. toctree::",
        "   :maxdepth: 1",
        "",
    ]
    for notebook in notebooks:
        relative_path = notebook.relative_to(notebook_target).with_suffix("")
        title = notebook.stem.replace("_", " ").title()

        notebook_data = json.loads(notebook.read_text(encoding="utf-8"))
        has_title = any(
            line.startswith("# ")
            for cell in notebook_data.get("cells", [])
            if cell.get("cell_type") == "markdown"
            for line in (
                "".join(cell.get("source", []))
                if isinstance(cell.get("source", []), list)
                else cell.get("source", "")
            ).splitlines()
        )
        if not has_title:
            notebook_data["cells"].insert(
                0,
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [f"# {title}\n"],
                },
            )
            notebook.write_text(
                json.dumps(notebook_data, ensure_ascii=False, indent=1) + "\n",
                encoding="utf-8",
            )

        toctree.append(f"   {title} <{relative_path.as_posix()}>")

    (notebook_target / "index.rst").write_text(
        "\n".join(toctree) + "\n",
        encoding="utf-8",
    )


def setup(app):
    app.connect("builder-inited", _sync_example_notebooks)

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_book_theme"
html_static_path = ["_static"]
html_favicon = "_static/icon.png"

html_css_files = [
    "custom.css",
]

html_theme_options = {
    "home_page_in_toc": True,
    "show_navbar_depth": 1,
    "navigation_with_keys": True,
    "use_download_button": False,
    "toc_title": "En esta página",
    "show_toc_level": 1,
    "show_prev_next": True,
    "search_bar_text": "Buscar...",
    # Logo (opcional)
    # "logo": {
    #     "image_light": "_static/logo-light.png",
    #     "image_dark": "_static/logo-dark.png",
    # },
    # Syntax highlighting
    "pygments_light_style": "tango",
    "pygments_dark_style": "monokai",
}

html_title = "Proximity Graphs Documentation"


html_context = {"default_mode": "light"}
