import os
import sys

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath(os.path.join('..', '..')))
sys.path.insert(0, os.path.abspath('../src'))
sys.path.insert(0, os.path.abspath('src'))
sys.path.insert(0, os.path.abspath('../src/pyharborcli'))
sys.path.insert(0, os.path.abspath('src/pyharborcli'))

project = 'pyharborcli'
author = 'alexeev-prog'
version = '0.10'
release = '0.1.0'
project_copyright = '2025, Alexeev Bronislaw'

extensions = [
    'sphinx.ext.autodoc',  # autodoc from docstrings
    'sphinx.ext.viewcode',  # links to source code
    'sphinx.ext.napoleon',  # support google and numpy docs style
    'sphinx.ext.todo',  # support TODO
    'sphinx.ext.coverage',  # check docs coverage
    'sphinx.ext.ifconfig',  # directives in docs
    'sphinx.ext.autosummary',  # generating summary for code
    'sphinx.ext.intersphinx',
    'sphinx.ext.githubpages',
]

pygments_style = 'gruvbox-dark'

html_theme = 'furo'  # theme
todo_include_todos = True  # include todo in docs
auto_doc_default_options = {'autosummary': True}

autodoc_mock_imports = []
autodoc_typehints = 'description'
autodoc_member_order = 'bysource'
autosummary_generate = True
napoleon_include_init_with_doc = True

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
}


def skip(app, what, name, obj, would_skip, options):
    if name == '__init__':
        return False
    return would_skip


def setup(app):
    app.connect('autodoc-skip-member', skip)
