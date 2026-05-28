# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Proximity Graphs"
copyright = "2025, Héctor Maravillo"
author = "Héctor Maravillo , Diego Villarreal , Heriberto Espino"
release = "v0.1.0a1"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_parser",
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
    ".md": "markdown",
}

templates_path = ["_templates"]
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_book_theme"
html_static_path = ["_static"]

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
