"""
Mocks the subprocess utils so we can test our interface to pytrebase rather than
pyrebase itself.

Created on Oct 8, 2019

@author: doublethefish
"""
import sys
import types


_CHECK_OUTPUT_FAILS = False


class FailExecuteGuard(object):
    """ creates and deletes a tmp-dir compatible with python2 and 3 """

    def __init__(self):
        self.prev = None

    def __enter__(self):
        global _CHECK_OUTPUT_FAILS
        self.prev = _CHECK_OUTPUT_FAILS
        _CHECK_OUTPUT_FAILS = True
        return self

    def __exit__(self, x_type, x_value, x_traceback):
        global _CHECK_OUTPUT_FAILS
        _CHECK_OUTPUT_FAILS = self.prev


class CalledProcessError(Exception):
    def __init__(self):
        self.output = "dummy output"
        self.returncode = 9


def failing_call(_cmd, **args):
    if _CHECK_OUTPUT_FAILS:
        raise CalledProcessError()


SUBPROCESS_MODULE_NAME = "subprocess"
SUBPROCESS_MOCK = types.ModuleType(SUBPROCESS_MODULE_NAME)
sys.modules[SUBPROCESS_MODULE_NAME] = SUBPROCESS_MOCK
SUBPROCESS_MOCK.check_output = failing_call
SUBPROCESS_MOCK.CalledProcessError = CalledProcessError
