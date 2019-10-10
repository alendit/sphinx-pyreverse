#!/usr/bin/env python
"""
Created on Oct 2, 2012

@author: alendit
"""
import os
from setuptools import setup


def read(fname):
    """ Reads a file in from disk and returns its contents """
    with open(os.path.join(os.path.dirname(__file__), fname), "r") as file_handle:
        return file_handle.read()


setup(
    name="sphinx-pyreverse",
    version="0.0.11",
    author="Dimitri Vorona",
    author_email="vorona@in.tum.de",
    description=(
        "A simple sphinx extension to generate " "UML diagrams with pyreverse"
    ),
    license="GPLv3",
    keywords="sphinx extension uml pyreverse",
    url="https://github.com/alendit/sphinx-pyreverse",
    long_description=read("README.rst"),
    packages=["sphinx_pyreverse"],
    install_requires=["sphinx", "docutils"],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python",
        "Topic :: Utilities",
    ],
)
