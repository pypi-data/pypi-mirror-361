# Configuration file for the Sphinx documentation builder.

# -- Project information -----------------------------------------------------

project = 'uubed'
copyright = '2025, uubed contributors'
author = 'uubed contributors'
release = '1.0.5'

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx_copybutton',
    'myst_parser',
]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_book_theme'
html_static_path = ['_static']

html_theme_options = {
    "repository_url": "https://github.com/twardoch/uubed",
    "use_repository_button": True,
    "use_edit_page_button": True,
    "path_to_docs": "docs/source",
}

# -- Extension configuration -------------------------------------------------

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
}

myst_enable_extensions = [
    "deflist",
    "colon_fence",
]