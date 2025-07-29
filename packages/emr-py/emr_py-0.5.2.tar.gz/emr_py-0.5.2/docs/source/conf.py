import importlib.metadata as md
import os
import sys

sys.path.insert(0, os.path.abspath("../../src"))

project = "emr-py"
copyright = "2025, Ezequiel M Rivero"
author = "Ezequiel M Rivero"

release = md.version("emr-py")

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",  # for Google/NumPy docstrings
    "sphinx_autodoc_typehints",  # for type hints in docs
]

autosummary_generate = True

autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
}

templates_path = ["_templates"]
exclude_patterns = ["Thumbs.db", ".DS_Store"]

language = "en"

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
