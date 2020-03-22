"""
Created on Oct 1, 2012

@author: alendit
"""
import os

__all__ = ["UMLGenerateDirective"]

from .uml_generate_directive import UMLGenerateDirective


def setup(app):
    """Setup directive"""
    # Allow override of the directive, defaulting to 'uml'
    directive_name_to_use = os.environ.get("SPHINX_PYREVERSE_DIRECTIVE", "uml")
    app.add_directive(directive_name_to_use, UMLGenerateDirective)
