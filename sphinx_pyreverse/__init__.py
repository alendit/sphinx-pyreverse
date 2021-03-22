"""
Created on Oct 1, 2012

@author: alendit
"""
import os

__all__ = ["UMLGenerateDirective"]

from .uml_generate_directive import UMLGenerateDirective


def setup(app):
    """Setup directive"""
    app.add_config_value("sphinx_pyreverse_output", default="png", rebuild="env")
    app.add_config_value("sphinx_pyreverse_filter_mode", default=None, rebuild="env")
    app.add_config_value("sphinx_pyreverse_class", default=None, rebuild="env")
    app.add_config_value("sphinx_pyreverse_show_ancestors", default=None, rebuild="env")
    app.add_config_value("sphinx_pyreverse_all_ancestors", default=None, rebuild="env")
    app.add_config_value(
        "sphinx_pyreverse_show_associated", default=None, rebuild="env"
    )
    app.add_config_value("sphinx_pyreverse_all_associated", default=None, rebuild="env")
    app.add_config_value("sphinx_pyreverse_show_builtin", default=None, rebuild="env")
    app.add_config_value("sphinx_pyreverse_module_names", default=None, rebuild="env")
    app.add_config_value(
        "sphinx_pyreverse_only_classnames", default=None, rebuild="env"
    )
    app.add_config_value("sphinx_pyreverse_ignore", default=None, rebuild="env")

    # Allow override of the directive, defaulting to 'uml'
    directive_name_to_use = os.environ.get("SPHINX_PYREVERSE_DIRECTIVE", "uml")
    app.add_directive(directive_name_to_use, UMLGenerateDirective)

    return {"parallel_read_safe": True}
