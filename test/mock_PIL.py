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


def _open(_):
    """ returns a dummy image with a size paramter """

    class MockImage:
        """ A MockImage with a mock size """

        def __init__(self):
            self.size = [0, 0]

    return MockImage()


PIL_MOCK.Image = Mock(name=PIL_MODULE_NAME + ".Image")
PIL_MOCK.Image.open = _open
