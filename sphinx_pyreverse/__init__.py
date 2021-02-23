"""
Created on Oct 1, 2012

@author: alendit
"""

__all__ = ["UMLGenerateDirective"]

from .uml_generate_directive import UMLGenerateDirective


def setup(app):
    """Setup directive"""
    app.add_directive("uml", UMLGenerateDirective)
    
    return {
        'parallel_read_safe': True
    }
