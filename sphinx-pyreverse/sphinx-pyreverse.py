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
import shutil
import tempfile

DIR_NAME = "uml_images"
UML_DIR = os.path.abspath(DIR_NAME)
print os.listdir(".")
if os.path.basename(UML_DIR) not in os.listdir("."):
    os.mkdir(UML_DIR)

class UMLDiagramm(nodes.General, nodes.Element):
    pass

class UMLGenerateDirective(Directive):
    required_arguments = 1
    optional_arguments = 0
    has_content = False
    
    def run(self):
        env = self.state.document.settings.env
        env.uml_dir = UML_DIR
        module_path = self.arguments[0]
        print "#" * 10
        print module_path
        print UML_DIR
        old_dir = os.getcwd()
        os.chdir(UML_DIR)
        basename = os.path.basename(module_path).split(".")[0]
        print call(['pyreverse', '-o', 'png', '-p', basename, os.path.abspath(os.path.join(old_dir, module_path))])
        
        uri = directives.uri(os.path.join(DIR_NAME, "classes_{0}.png".format(basename)))
        print uri
        img = nodes.image(uri=uri, scale="50")
        os.chdir(old_dir)
        return [img]

def visit_uml_node(self, node):
    self.visit_image(node)

def depart_uml_node(self, node):
    self.depart_image(node)
    
    
def process_uml_nodes():
    pass

def clean_uml(app, exception):
    shutil.rmtree(UML_DIR)
    pass


def setup(app):
    app.add_node(UMLDiagramm,
                 html=(visit_uml_node, depart_uml_node),
                 )

    app.add_directive('uml', UMLGenerateDirective)
    app.connect("build-finished", clean_uml)
