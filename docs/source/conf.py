"""Configuration file for the Sphinx documentation builder."""

import sys
import os

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath('../..'))

project = "Contact Management REST API"
copyright = "2025, mariashubna"
author = "mariashubna"

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon"
]

# Napoleon settings
napoleon_google_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = True

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
html_theme = "nature"
html_static_path = ["_static"]

# Autodoc settings
autodoc_member_order = 'bysource'
autodoc_typehints = 'description'
add_module_names = False
