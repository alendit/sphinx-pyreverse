'''
Created on Oct 1, 2012

@author: alendit
'''
from docutils import nodes
from sphinx.util.compat import Directive
from sphinx.util.compat import make_admonition
from subprocess import call

class UMLDiagramm(nodes.General, nodes.Element):
    pass

class UMLGenerateDirective(Directive):
    has_content = True
    
    def run(self):
        module_path = self.content[0]
        call(['pyreverse', '-o', 'png', '-p','output', "models.py"])
        img = nodes.image(uri="classes_output.png", scale="50")
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
                 )

    app.add_directive('uml', UMLGenerateDirective)
