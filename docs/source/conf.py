import datetime
import pathlib
import sys

project = 'hwloc-xml-parser'
author = 'Tomasetti, R and Arnst, M.'
copyright = f'{datetime.datetime.now().year}, {author}'

PROJECT_DIR = pathlib.Path(__file__).parent.parent.parent

sys.path.append(str(PROJECT_DIR))

from hwloc_xml_parser import __version__
release = __version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.apidoc',
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
]

intersphinx_mapping = {
    'python' : ('https://docs.python.org/3', None),
}

apidoc_modules = [
    {
        'path' : PROJECT_DIR / 'hwloc_xml_parser',
        'destination' : 'api',
        'max_depth' : 4,
        'implicit_namespaces' : True,
    }
]

autodoc_default_options = {
    'members' : True,
    'show-inheritance' : True,
    'undoc-members' : True,
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'

# Some references are broken, or the package does not provide an object inventory file.
# See also https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-nitpick_ignore_regex.
nitpick_ignore_regex = [
    ('py:class', 'Element'),
]
