# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import datetime
import importlib.metadata
import os
import re
import sys

import django
from django.conf import settings

docs_dir = os.path.dirname(os.path.abspath(__file__))
ext_dir = os.path.join(docs_dir, '_ext')
project_dir = os.path.join(docs_dir, '..', '..')
src_dir = os.path.join(project_dir, 'src')

sys.path.insert(0, src_dir)
sys.path.insert(0, ext_dir)

settings.configure()
django.setup()

# -- Project information -----------------------------------------------------

package_name = 'momotor-django'
project = 'Momotor Django'
copyright = '2019-%d, Eindhoven University of Technology' % datetime.datetime.now().year
author = 'E.T.J. Scheffers'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The full version, including alpha/beta/rc tags.
release = importlib.metadata.version(package_name)
# The short X.Y version.
version = re.match(r'\d+\.\d+', release).group(0)


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'djangoroles',
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx_autodoc_typehints',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

rst_epilog = """
.. _Momotor: https://momotor.org/
"""

# -- Options for autodoc -----------------------------------------------------

autodoc_member_order = 'groupwise'

# -- Options for intersphinx -------------------------------------------------


def inventory(domain, name):
    # Try to collect intersphinx mapping from development environment first, then from online version

    local_project = None
    if domain == 'engine':
        local_project = os.path.join(project_dir, '..', name)

    if local_project:
        local_inv = os.path.join(local_project, 'docs', 'build', name, 'objects.inv')
        if os.path.exists(local_inv):
            return f'/momotor/docs/build/{name}', local_inv

    if 'rc' in release:
        # Since this package is a dev release, use dev releases for intersphinx too
        return f'https://momotor.org/doc/{domain}/{name}/dev/latest/', None

    return f'https://momotor.org/doc/{domain}/{name}/', None


intersphinx_mapping = {
    'django': ('https://docs.djangoproject.com/en/4.2/', 'https://docs.djangoproject.com/en/4.2/_objects/'),
    'grpclib': ('https://grpclib.readthedocs.io/en/latest/', None),
    'protobuf': ('https://googleapis.dev/python/protobuf/latest/', None),
    'python': ('https://docs.python.org/3', None),
    'momotor-engine-proto': inventory('engine', 'momotor-engine-proto'),
    'momotor-engine-shared': inventory('engine', 'momotor-engine-shared'),
}

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'furo'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

html_copy_source = False

html_theme_options = {
    "light_logo": "logo-text.png",
    "dark_logo": "logo-text-negative.png",
}

html_context = {
    'project_url': 'https://momotor.org/',
    'pypi_url': 'https://pypi.org/project/momotor-django/',
    'repository_url': 'https://gitlab.tue.nl/momotor/engine-py3/momotor-django/',
}

html_sidebars = {
    "**": [
        "sidebar/brand.html",
        "sidebar/search.html",
        "sidebar/scroll-start.html",
        "sidebar/navigation.html",
        "sidebar/scroll-end.html",
        "sidebar/variant-selector.html",
        "projectlinks.html",
    ]
}
