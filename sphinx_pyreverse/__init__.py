'''
Created on Oct 1, 2012

@author: alendit
'''

from __future__ import print_function

from docutils import nodes
from docutils.parsers.rst import directives
try:
    from sphinx.util.compat import Directive
except ImportError:
    from docutils.parsers.rst import Directive
from subprocess import call
import os

try:
    from PIL import Image as IMAGE
except ImportError as error:
    IMAGE = None

# debugging with IPython
#~ try:
    #~ from IPython import embed
#~ except ImportError as e:
    #~ pass


class UMLGenerateDirective(Directive):
    """UML directive to generate a pyreverse diagram"""
    required_arguments = 1
    optional_arguments = 2
    has_content = False
    DIR_NAME = "uml_images"
    # a list of modules which have been parsed by pyreverse
    generated_modules = []

    def run(self):
        doc = self.state.document
        env = doc.settings.env
        # the top-level source directory
        self.base_dir = env.srcdir
        # the directory of the file calling the directive
        self.src_dir = os.path.dirname(doc.current_source)
        self.uml_dir = os.path.abspath(os.path.join(self.base_dir, self.DIR_NAME))

        if not os.path.exists(self.uml_dir):
            os.mkdir(self.uml_dir)

        env.uml_dir = self.uml_dir
        self.module_name = self.arguments[0]

        if self.module_name not in self.generated_modules:
            print(call(['pyreverse', '-o', 'png', '-p', self.module_name, self.module_name], cwd=self.uml_dir))
            # avoid double-generating
            self.generated_modules.append(self.module_name)

        valid_flags = {':classes:', ':packages:'}
        unkown_arguments = set(self.arguments[1:]) - valid_flags
        if unkown_arguments:
            raise ValueError('invalid flags encountered: {0}. Must be one of {1}' \
                             .format(unkown_arguments, valid_flags))

        res = []
        for arg in self.arguments[1:]:
            img_name = arg.strip(':')
            res.append(self.generate_img(img_name))

        return res

    def generate_img(self, img_name):
        path_from_base = os.path.join(self.DIR_NAME, "{1}_{0}.png").format(self.module_name, img_name)
        # relpath is necessary to allow generating from a sub-directory of the main 'source'
        uri = directives.uri(os.path.join(
            os.path.relpath(self.base_dir, start=self.src_dir),
            path_from_base
        ))
        scale = 100
        max_width = 1000
        if IMAGE:
            i = IMAGE.open(os.path.join(self.base_dir, path_from_base))
            image_width = i.size[0]
            if image_width > max_width:
                scale = max_width * scale / image_width
        return nodes.image(uri=uri, scale=scale)

def setup(app):
    """Setup directive"""
    app.add_directive('uml', UMLGenerateDirective)
