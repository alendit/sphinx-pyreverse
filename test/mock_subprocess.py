"""
Mocks the subprocess utils so we can test our interface to pytrebase rather than
pyrebase itself.

Created on Oct 8, 2019

@author: doublethefish
"""
import sys
import types
from mock import MagicMock


_CHECK_OUTPUT_FAILS = False


class FailExecuteGuard(object):
    """ When in scope, causes the subprocess mock to fail """

    def __init__(self):
        self.prev = None

    def __enter__(self):
        # This is a bit of hack for testing purposes, means we can only do
        # single-threaded testing
        global _CHECK_OUTPUT_FAILS  # pylint: disable=global-statement
        self.prev = _CHECK_OUTPUT_FAILS
        _CHECK_OUTPUT_FAILS = True
        return self

    def __exit__(self, x_type, x_value, x_traceback):
        # This is a bit of hack for testing purposes, means we can only do
        # single-threaded testing
        global _CHECK_OUTPUT_FAILS  # pylint: disable=global-statement
        _CHECK_OUTPUT_FAILS = self.prev


class CalledProcessError(Exception):
    """ Mock the exception thrown by subprocess """

    def __init__(self):
        super(CalledProcessError, self).__init__()
        self.output = "dummy output"
        self.returncode = 9


def failing_call(_cmd, **args):
    """ Replaces subprocess check_output()

    When check_output is called, and we are inside the scope of a FailExecuteGuard we
    raise a CalledProcessError exception """

    if _CHECK_OUTPUT_FAILS:
        raise CalledProcessError()


SUBPROCESS_MODULE_NAME = "subprocess"
SUBPROCESS_MOCK = types.ModuleType(SUBPROCESS_MODULE_NAME)
sys.modules[SUBPROCESS_MODULE_NAME] = SUBPROCESS_MOCK
SUBPROCESS_MOCK.check_output = failing_call
SUBPROCESS_MOCK.CalledProcessError = CalledProcessError
SUBPROCESS_MOCK.PIPE = MagicMock()
SUBPROCESS_MOCK.STDOUT = MagicMock()
SUBPROCESS_MOCK.DEVNULL = MagicMock()
