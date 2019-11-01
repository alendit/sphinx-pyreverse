"""
Mocks PIL utils so we can test the workers without installing PIL/Image

Created on Oct 8, 2019

@author: doublethefish
"""
import sys
import types
from mock import Mock

PIL_MODULE_NAME = "PIL"
PIL_MOCK = types.ModuleType(PIL_MODULE_NAME)
sys.modules[PIL_MODULE_NAME] = PIL_MOCK

_DIMS_UNDER_TEST = (0, 0)


class DimsUnderTestGuard(object):
    """ Changes the width to use in tests """

    def __init__(self, width=0, height=0):
        self._prev = None
        self._dims = (width, height)

    def __enter__(self):
        global _DIMS_UNDER_TEST
        self._prev = _DIMS_UNDER_TEST
        _DIMS_UNDER_TEST = self._dims

        return self

    def __exit__(self, x_type, x_value, x_traceback):
        global _DIMS_UNDER_TEST
        _DIMS_UNDER_TEST = self._prev


def _open(_):
    """ returns a dummy image with a size paramter """

    class MockImage:
        """ A MockImage with a mock size """

        def __init__(self):
            self.size = _DIMS_UNDER_TEST

    return MockImage()


PIL_MOCK.Image = Mock(name=PIL_MODULE_NAME + ".Image", open=_open)
