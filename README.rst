Sphinx-pyreverse
=================

.. image:: https://circleci.com/gh/alendit/sphinx-pyreverse.svg?style=svg
    :target: https://circleci.com/gh/alendit/sphinx-pyreverse

.. image:: https://badge.fury.io/py/sphinx-pyreverse.svg
    :target: https://badge.fury.io/py/sphinx-pyreverse

A simple sphinx extension to generate a UML diagram from python modules.

Install
--------

Install with:::

    pip install sphinx-pyreverse

Usage
------

Add "sphinx_pyreverse" to the extensions list in your conf.py (make sure it is
in the PYTHONPATH).

Call the directive with path to python module as content. The ``:classes:`` and
``:packages:`` flags specify which UML diagrams to show.::

    .. uml:: {{modulename}}
        :classes:
        :packages:

Requires pyreverse from pylint.

Options
^^^^^^^

To configure usage, in your conf.py

* ``sphinx_pyreverse_output`` (see --output), default is "png"
* ``sphinx_pyreverse_filter_mode`` (see --filter_mode), default is None
* ``sphinx_pyreverse_class`` (see --class), default is None
* ``sphinx_pyreverse_show_ancestors`` (see --show_ancestors), default is None
* ``sphinx_pyreverse_all_ancestors`` (see --all_ancestors), default is None
* ``sphinx_pyreverse_show_associated`` (see --show_associated), default is None
* ``sphinx_pyreverse_all_associated`` (see --all_associated), default is None
* ``sphinx_pyreverse_show_builtin`` (see --show_builtin), default is None
* ``sphinx_pyreverse_module_names`` (see --module_names), default is None
* ``sphinx_pyreverse_only_classnames`` (see --only_classnames), default is None
* ``sphinx_pyreverse_ignore`` (see --ignore), default is None

Changing the directive
^^^^^^^^^^^^^^^^^^^^^^

To override the directive, which defaults to 'uml' set the
``SPHINX_PYREVERSE_DIRECTIVE`` environment variable to whatever you like.
