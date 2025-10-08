"""
Sphinx configuration file for Sensory Tracer Science documentation.

This configuration enables scientific documentation standards including:
- Mathematical notation rendering (MathJax)
- Bibliography management (sphinxcontrib-bibtex)
- API documentation (autodoc)
- Cross-references and citations
"""

import os
import sys
from datetime import datetime

# Add the package to the Python path
sys.path.insert(0, os.path.abspath('../'))
sys.path.insert(0, os.path.abspath('../sensory_tracer_science'))

# -- Project information -----------------------------------------------------
project = 'Sensory Tracer Science'
copyright = f'{datetime.now().year}, STS Development Team'
author = 'STS Development Team'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'sphinx.ext.napoleon',
    'sphinxcontrib.bibtex',
    'myst_parser',
]

# Bibliography configuration
bibtex_bibfiles = ['references.bib']
bibtex_default_style = 'alpha'
bibtex_reference_style = 'author_year'

# Templates path
templates_path = ['_templates']

# Source file suffixes
source_suffix = {
    '.rst': None,
    '.md': 'myst_parser',
}

# Master document
master_doc = 'index'

# Language
language = 'en'

# Exclude patterns
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Pygments style
pygments_style = 'sphinx'

# -- Options for HTML output ------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'analytics_id': '',
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}

html_static_path = ['_static']
html_css_files = ['custom.css']

# -- Options for LaTeX output -----------------------------------------------
latex_engine = 'pdflatex'
latex_elements = {
    'papersize': 'a4paper',
    'pointsize': '10pt',
    'preamble': r'''
\usepackage{amsmath}
\usepackage{amsfonts}
\usepackage{amssymb}
\usepackage{physics}
\usepackage{siunitx}
    ''',
}

# Grouping the document tree into LaTeX files
latex_documents = [
    (master_doc, 'SensoryTracerScience.tex', 'Sensory Tracer Science Documentation',
     'STS Development Team', 'manual'),
]

# -- Options for manual page output ------------------------------------------
man_pages = [
    (master_doc, 'sensory-tracer-science', 'Sensory Tracer Science Documentation',
     [author], 1)
]

# -- Options for Texinfo output ----------------------------------------------
texinfo_documents = [
    (master_doc, 'SensoryTracerScience', 'Sensory Tracer Science Documentation',
     author, 'SensoryTracerScience', 'Physics-based sensory tracer analysis framework.',
     'Miscellaneous'),
]

# -- Extension configuration -------------------------------------------------

# autodoc configuration
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

# autosummary configuration
autosummary_generate = True
autosummary_imported_members = True

# Napoleon configuration (Google/NumPy docstring style)
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# Intersphinx configuration
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'scipy': ('https://docs.scipy.org/doc/scipy/', None),
    'matplotlib': ('https://matplotlib.org/stable/', None),
}

# MathJax configuration
mathjax3_config = {
    'tex': {
        'inlineMath': [['$', '$'], ['\\(', '\\)']],
        'displayMath': [['$$', '$$'], ['\\[', '\\]']],
        'processEscapes': True,
        'processEnvironments': True,
    },
    'options': {
        'ignoreHtmlClass': 'tex2jax_ignore',
        'processHtmlClass': 'tex2jax_process',
    }
}

# Todo configuration
todo_include_todos = True

# Coverage configuration
coverage_show_missing_items = True