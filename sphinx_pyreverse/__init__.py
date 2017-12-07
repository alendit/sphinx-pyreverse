'''
Created on Oct 1, 2012

@author: alendit
'''

from __future__ import print_function

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.util.compat import Directive
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

    option_spec = {'classes': directives.unchanged,
                   'packages': directives.unchanged,
                   'show-ancestors': directives.nonnegative_int,
                   'show-associated': directives.nonnegative_int,
                   }

    def run(self):
        doc = self.state.document
        env = doc.settings.env
        # the top-level source directory
        self.base_dir = env.srcdir
        # the directory of the file calling the directive
        self.src_dir = os.path.dirname(doc.current_source)
        self.uml_dir = os.path.abspath(os.path.join(self.base_dir, self.DIR_NAME))
        #print("--- {}".format(self.arguments[0]))
        #print("\tDIR_NAME {}".format(self.DIR_NAME))
        #print("\toptions {}".format(self.options))

        if not os.path.exists(self.uml_dir):
            os.mkdir(self.uml_dir)

        env.uml_dir = self.uml_dir
        self.module_name = self.arguments[0]
        
        if self.module_name not in self.generated_modules:
            cmd = ['pyreverse', '-o', 'png', '-p', self.module_name]
            if 'show-ancestors' in self.options:
                cmd.append("-a")
                cmd.append(str(self.options['show-ancestors']))
            if 'show-associated' in self.options:
                cmd.append("-s")
                cmd.append(str(self.options['show-associated']))
            cmd.append(self.module_name)
            #print("\tExecuting {}".format(" ".join(cmd)))
            res = call(cmd, cwd=self.uml_dir)
            #print("\tresult", res)
            # avoid double-generating
            self.generated_modules.append(self.module_name)
        
        # print(self.arguments)
        valid_flags = {'classes', 'packages'}
        flags = set(self.options) & valid_flags
        if len(flags) != 1:
            raise ValueError('invalid flag encountered. must be one of {0}'.format(valid_flags))
        
        res = []
        for arg in flags:
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
