# ================================================================================
# F3.6: SPHINX DOCUMENTATION CONFIGURATION
# ================================================================================
# 
# 🎯 **AMAÇ:** Professional documentation generation
# 📋 **KAPSAM:** API docs, tutorials, examples
# 🔧 **ENTEGRASYON:** ReadTheDocs compatibility
# 
# ================================================================================

# Configuration file for the Sphinx documentation builder.
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Blackjack AI Simulation'
copyright = '2024, Blackjack AI Team'
author = 'Blackjack AI Team'
release = '3.0.0'
version = '3.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx.ext.mathjax',
    'sphinx.ext.githubpages',
    'sphinx_rtd_theme',
    'myst_parser',
    'sphinx_autodoc_typehints',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The suffix of source filenames.
source_suffix = {
    '.rst': 'restructuredtext',
    '.txt': 'markdown',
    '.md': 'markdown',
}

# The master toctree document.
master_doc = 'index'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'navigation_depth': 4,
    'titles_only': False,
    'collapse_navigation': False,
    'sticky_navigation': True,
    'includehidden': True,
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': True,
    'style_nav_header_background': '#2980B9',
}

html_static_path = ['_static']
html_css_files = [
    'custom.css',
]

# -- Options for autodoc ----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#configuration

autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__',
    'show-inheritance': True,
    'inherited-members': True,
}

autodoc_typehints = 'description'
autodoc_typehints_description_target = 'documented'

# -- Options for napoleon ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html#configuration

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

# -- Options for intersphinx mapping ----------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html#configuration

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
    'matplotlib': ('https://matplotlib.org/stable/', None),
    'gymnasium': ('https://gymnasium.farama.org/', None),
    'stable-baselines3': ('https://stable-baselines3.readthedocs.io/', None),
    'torch': ('https://pytorch.org/docs/stable/', None),
    'optuna': ('https://optuna.readthedocs.io/', None),
    'ray': ('https://docs.ray.io/', None),
}

# -- Options for todo extension ---------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/todo.html#configuration

todo_include_todos = True

# -- Options for coverage extension -----------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/coverage.html#configuration

coverage_show_missing_items = True

# -- Options for GitHub Pages -----------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/githubpages.html#configuration

html_baseurl = 'https://blackjack-ai-sim.readthedocs.io/'

# -- Custom configuration ---------------------------------------------------

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Custom CSS
def setup(app):
    app.add_css_file('custom.css') 