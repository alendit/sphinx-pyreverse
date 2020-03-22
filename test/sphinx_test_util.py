"""
Defines mocks objects mimicing sphinx applications state for tests

Created on 22, 2020

@author: doublethefish
"""


class MockConfig(object):  # pylint: disable=missing-docstring
    def __init__(self):  # pylint: disable=missing-docstring
        self.sphinx_pyreverse_output = "png"


class MockEnv(object):  # pylint: disable=missing-docstring
    def __init__(self):  # pylint: disable=missing-docstring
        self.srcdir = "."
        self.config = MockConfig()


class MockDocSettings(object):  # pylint: disable=missing-docstring
    def __init__(self):  # pylint: disable=missing-docstring
        self.env = MockEnv()


class MockDoc(object):  # pylint: disable=missing-docstring
    def __init__(self):  # pylint: disable=missing-docstring
        self.settings = MockDocSettings()
        self.current_source = "."


class MockState(object):  # pylint: disable=missing-docstring
    def __init__(self):  # pylint: disable=missing-docstring
        self.document = MockDoc()
