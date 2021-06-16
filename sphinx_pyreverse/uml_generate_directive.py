"""
Defines sphinx-wrappers for the pyreverse tool

First, Created on Oct 1, 2012, this file created on Oct 8, 2019

@author: alendit, doublethefish
"""

import copy
import os
import subprocess
import sys

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.util import logging

try:
    from sphinx.util.compat import Directive
except ImportError:
    from docutils.parsers.rst import Directive  # pylint: disable=C0412

try:
    from PIL import Image as IMAGE
except ImportError:  # pragma: no cover
    IMAGE = None

# debugging with IPython
# ~ try:
# ~ from IPython import embed
# ~ except ImportError as e:
# ~ pass


def subproc_wrapper(*args, **kwargs):  # pragma: no cover
    """A shim which allows mocking of the subproc call when using pytest"""
    subprocess.check_output(*args, **kwargs)


class UMLGenerateDirective(Directive):
    """UML directive to generate a pyreverse diagram"""

    required_arguments = 1
    optional_arguments = 2
    has_content = False
    DIR_NAME = "uml_images"
    # a list of modules which have been parsed by pyreverse
    generated_modules = []

    def _validate(self):
        """Validates that the RST parameters are valid"""
        valid_flags = {":classes:", ":packages:"}
        unkown_arguments = set(self.arguments[1:]) - valid_flags
        if unkown_arguments:
            raise ValueError(
                "invalid flags encountered: {0}. Must be one of {1}".format(
                    unkown_arguments, valid_flags
                )
            )

    def _build_command(self, module_name, config):  # noqa: C901 func too-complex
        cmd = [
            "pyreverse",
            "--output",
            config.sphinx_pyreverse_output,
            "--project",
            module_name,
        ]
        if config.sphinx_pyreverse_filter_mode:
            assert config.sphinx_pyreverse_filter_mode
            cmd.extend(("--filter-mode", config.sphinx_pyreverse_filter_mode))
        if config.sphinx_pyreverse_class:
            cmd.extend(("--class", config.sphinx_pyreverse_class))
        if config.sphinx_pyreverse_show_ancestors:
            cmd.extend(("--show-ancestors", config.sphinx_pyreverse_show_ancestors))
        if config.sphinx_pyreverse_all_ancestors:
            cmd.append("--all-ancestors")
        if config.sphinx_pyreverse_show_associated:
            cmd.extend(("--show-associated", config.sphinx_pyreverse_show_associated))
        if config.sphinx_pyreverse_all_associated:
            cmd.append("--all-associated")
        if config.sphinx_pyreverse_show_builtin:
            cmd.append("--show-builtin")
        if config.sphinx_pyreverse_module_names:
            cmd.extend(("--module-names", config.sphinx_pyreverse_module_names))
        if config.sphinx_pyreverse_only_classnames:
            cmd.append("--only-classnames")
        if config.sphinx_pyreverse_ignore:
            cmd.extend(("--ignore", config.sphinx_pyreverse_ignore))

        # finally append the module to generate the uml for
        cmd.append(module_name)
        return cmd

    def run(self):
        doc = self.state.document
        env = doc.settings.env
        # the top-level source directory
        base_dir = env.srcdir
        # the directory of the file calling the directive
        src_dir = os.path.dirname(doc.current_source)
        uml_dir = os.path.abspath(os.path.join(base_dir, self.DIR_NAME))

        if not os.path.exists(uml_dir):
            os.mkdir(uml_dir)

        env.uml_dir = uml_dir
        module_name = self.arguments[0]

        self._validate()

        if module_name not in self.generated_modules:
            cmd = self._build_command(module_name, env.config)
            logging.getLogger(__name__).info(
                "sphinx-pyreverse: Running: {cmd}".format(cmd=" ".join(cmd))
            )

            # Ensure we have the right paths available to the pyreverse subproc
            if "PYTHONPATH" in os.environ:
                sub_proc_env = copy.deepcopy(os.environ)
            else:
                sub_proc_env = copy.deepcopy(os.environ)
                # TODO: check this is ok on windows etc.
                sub_proc_env["PYTHONPATH"] = ":".join(sys.path)

            try:
                subproc_wrapper(
                    cmd,
                    cwd=uml_dir,
                    env=sub_proc_env,  # use the calling-env for the subproc (paths etc)
                )
            except subprocess.CalledProcessError as error:
                for line in str(error.output).split("\\n"):
                    logging.getLogger(__name__).info(
                        "pyreverse-log: {line}".format(line=line)
                    )
                raise

            # avoid double-generating
            self.generated_modules.append(module_name)

        res = []
        for arg in self.arguments[1:]:
            img_name = arg.strip(":")
            res.append(
                self.generate_img(img_name, module_name, base_dir, src_dir, env.config)
            )

        return res

    def generate_img(self, img_name, module_name, base_dir, src_dir, config):
        """Resizes the image and returns a Sphinx image"""
        path_from_base = os.path.join(self.DIR_NAME, "{1}_{0}.{2}").format(
            module_name, img_name, config.sphinx_pyreverse_output
        )
        # use relpath to get sub-directory of the main 'source' location
        src_base = os.path.relpath(base_dir, start=src_dir)
        uri = directives.uri(os.path.join(src_base, path_from_base))
        scale = 100
        max_width = 1000
        if IMAGE:
            i = IMAGE.open(os.path.join(base_dir, path_from_base))
            image_width = i.size[0]
            if image_width > max_width:
                scale = max_width * scale / image_width
        else:
            logging.getLogger(__name__).warning(
                "sphinx-pyreverse: No image manipulation lib found!"
            )
        return nodes.image(uri=uri, scale=scale)
