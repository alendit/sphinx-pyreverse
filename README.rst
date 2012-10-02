Sphinx-pyreverse
=================

A simple sphinx extension to generate a UML diagram from python modules.

Usage
------

Call the directive with path to python module as content::

	.. uml::
		{{path to the module}}
        
Requires pyreverse from pylint.
