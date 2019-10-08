"""
Mocks the subprocess utils so we can test our interface to pytrebase rather than
pyrebase itself.

Created on Oct 8, 2019

@author: doublethefish
"""
import sys
import types
from mock import Mock

SUBPROCESS_MODULE_NAME = "subprocess"
SUBPROCESS_MOCK = types.ModuleType(SUBPROCESS_MODULE_NAME)
sys.modules[SUBPROCESS_MODULE_NAME] = SUBPROCESS_MOCK
SUBPROCESS_MOCK.call = Mock(name=SUBPROCESS_MODULE_NAME + ".call")
