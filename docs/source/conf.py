# Configuration file for the Sphinx documentation builder.

import os
import sys

sys.path.insert(0, os.path.abspath("../.."))

project = "ProximityGraphs"
copyright = "2026, Hector Maravillo"
author = "Hector Maravillo, Diego Villarreal, Heriberto Espino"
release = "0.1.0"

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.mathjax",
    "sphinx_autodoc_typehints",
]

myst_enable_extensions = [
    "deflist",
    "colon_fence",
    "dollarmath",
    "amsmath",
    "html_image",
]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

templates_path = ["_templates"]
exclude_patterns = []

html_theme = "sphinx_book_theme"
html_static_path = ["_static"]
