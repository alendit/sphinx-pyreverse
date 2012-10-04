#!/usr/bin/env python
'''
Created on Oct 2, 2012

@author: alendit
'''
from setuptools import setup
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name="sphinx-pyreverse",
      version="0.0.10",
      author="Dimitri Vorona",
      author_email="vorona@in.tum.de",
      description=("A simple sphinx extension to generate "
                    "UML diagrams with pyreverse"),
      license="GPLv3",
      keywords="sphinx extension uml pyreverse",
      url="https://github.com/alendit/sphinx-pyreverse",
      long_description=read('README.rst'),
      packages=['sphinx_pyreverse'],
      classifiers=[
                   'Development Status :: 2 - Pre-Alpha',
                   'Intended Audience :: Information Technology',
                   'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
                   'Programming Language :: Python',
                   'Topic :: Utilities',
                   ]
      )
