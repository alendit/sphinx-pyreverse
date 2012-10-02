'''
Created on Oct 1, 2012

@author: alendit
'''
from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.util.compat import Directive
from sphinx.util.compat import make_admonition
from subprocess import call
import os


class UMLGenerateDirective(Directive):
    required_arguments = 1
    optional_arguments = 0
    has_content = False
    
    def run(self):
        env = self.state.document.settings.env
        SRC_DIR = env.srcdir
        DIR_NAME = "uml_images"
        UML_DIR = os.path.join(SRC_DIR, DIR_NAME)
        
        if os.path.basename(UML_DIR) not in os.listdir(SRC_DIR):
            os.mkdir(UML_DIR)
        env.uml_dir = UML_DIR
        module_path = self.arguments[0]
        os.chdir(UML_DIR)
        basename = os.path.basename(module_path).split(".")[0]
        
        uri = directives.uri(os.path.join(DIR_NAME, "classes_{0}.png".format(basename)))
        img = nodes.image(uri=uri)
        os.chdir(SRC_DIR)
        return [img]

def visit_uml_node(self, node):
    self.visit_image(node)

def depart_uml_node(self, node):
    self.depart_image(node)
    
    
def process_uml_nodes():
    pass

def setup(app):
    app.add_node(UMLDiagramm,
                 html=(visit_uml_node, depart_uml_node),
                 latex=(visit_uml_node, depart_uml_node),
                 text=(visit_uml_node, depart_uml_node),
                 )

    app.add_directive('uml', UMLGenerateDirective)
