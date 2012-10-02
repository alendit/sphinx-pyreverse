'''
Created on Oct 1, 2012

@author: alendit
'''
from docutils import nodes
from sphinx.util.compat import Directive
from sphinx.util.compat import make_admonition
from subprocess import call
import os
import shutil

UML_DIR = "uml_images"

class UMLDiagramm(nodes.General, nodes.Element):
    pass

class UMLGenerateDirective(Directive):
    has_content = True
    
    def run(self):
        module_path = self.content[0]
        print "#" * 10
        print module_path
        if UML_DIR not in os.listdir("."):
            os.mkdir(UML_DIR)
        os.chdir(UML_DIR)
        basename = os.path.basename(module_path).split(".")[0]
        print call(['pyreverse', '-o', 'png', '-p', basename, os.path.join("..", module_path)])
        os.chdir("..")
        img = nodes.image(uri=os.path.join(UML_DIR, "classes_{0}.png".format(basename)), scale="50")
        return [img]

def visit_uml_node(self, node):
    self.visit_image(node)

def depart_uml_node(self, node):
    self.depart_image(node)
    
    
def process_uml_nodes():
    pass

def clean_uml(app, exception):
    shutil.rmtree(UML_DIR)


def setup(app):
    app.add_node(UMLDiagramm,
                 html=(visit_uml_node, depart_uml_node),
                 )

    app.add_directive('uml', UMLGenerateDirective)
    app.connect("build-finished", clean_uml)
