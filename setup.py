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
    version="0.0.14",
    author="Dimitri Vorona",
    author_email="vorona@in.tum.de",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python",
        "Topic :: Utilities",
    ],
    description=(
        "A simple sphinx extension to generate " "UML diagrams with pyreverse"
    ),
    extras_require={
        "deploy": [
            # deps for deploying
            "twine",
        ],
        "pil": [
            # because of the vaious ways of getting PIL we reccomend, but do
            # not enfore, pillow
            "pillow",
        ],
        "tests": [
            "coverage",
            "docutils",
            "flake8",
            "mock",
            "nose2",
            "pylint",
            "sphinx",
        ],
    },
    install_requires=[
        "docutils",
        "sphinx",
    ],
    keywords="sphinx extension uml pyreverse",
    license="GPLv3",
    long_description=read("README.rst"),
    packages=["sphinx_pyreverse"],
    url="https://github.com/alendit/sphinx-pyreverse",
)
