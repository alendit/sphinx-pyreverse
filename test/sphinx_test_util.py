"""
Defines mocks objects mimicing sphinx applications state for tests

Created on 22, 2020

@author: doublethefish
"""


class MockConfig(object):  # pylint: disable=missing-docstring
    def __init__(self):  # pylint: disable=missing-docstring
        self.sphinx_pyreverse_output = "png"
        self.sphinx_pyreverse_filter_mode = None
        self.sphinx_pyreverse_class = None
        self.sphinx_pyreverse_show_ancestors = None
        self.sphinx_pyreverse_all_ancestors = None
        self.sphinx_pyreverse_show_associated = None
        self.sphinx_pyreverse_all_associated = None
        self.sphinx_pyreverse_show_builtin = None
        self.sphinx_pyreverse_module_names = None
        self.sphinx_pyreverse_only_classnames = None
        self.sphinx_pyreverse_ignore = None


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
