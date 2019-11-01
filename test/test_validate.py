"""
Defines tests and mock to test the sphinx pyreverse tool

Created on Oct 8, 2019

@author: doublethefish
"""
import os
import unittest
import shutil
import tempfile

import test.mock_subprocess
import test.mock_pil
from mock import Mock
import sphinx_pyreverse
import sphinx_pyreverse.uml_generate_directive


class TempdirGuard(object):
    """ creates and deletes a tmp-dir compatible with python2 and 3 """

    def __init__(self):
        self.path = tempfile.mkdtemp(prefix="sphinx_pyreverse_test")

    def __enter__(self):
        return self

    def __exit__(self, x_type, x_value, x_traceback):
        shutil.rmtree(self.path)  # always clean up on exit


class TestUMLGenerateDirective(unittest.TestCase):
    """ A collection of tests for the UMLGenerateDirective object """

    def gen(self):
        """ Constructs and returns a mocked UMLGenerateDirectiver instance """

        class MockEnv:
            def __init__(self):
                self.srcdir = "."

        class MockDocSettings:
            def __init__(self):
                self.env = MockEnv()

        class MockDoc:
            def __init__(self):
                self.settings = MockDocSettings()
                self.current_source = "."

        class MockState:
            def __init__(self):
                self.document = MockDoc()

        return sphinx_pyreverse.UMLGenerateDirective(
            name="test",
            arguments=["noexist_module", ":classes:", ":packages:"],
            options=None,
            content=None,
            lineno=None,
            content_offset=None,
            block_text=None,
            state=MockState(),
            state_machine=None,
        )

    def test_ctor(self):
        """ simply constructs a UMLGenerateDirectiver instance with mock values """
        instance = self.gen()
        self.assertIsNotNone(instance)

    def test_run(self):
        """ simply invokes run with the default setup parameters """
        instance = self.gen()
        instance.run()

    def test_uml_dir_creation(self):
        """ test that the uml directory is created under the right circumstances

        This just captures current behaviour - there should be no problem changing it.
        """
        instance = self.gen()
        with TempdirGuard() as tempdir:
            mock_dir = os.path.join(tempdir.path, "noexist.dir")
            instance.state.document.settings.env.srcdir = mock_dir
            self.assertTrue(os.path.exists(tempdir.path))
            self.assertFalse(os.path.exists(mock_dir))
            try:
                FileNotFoundError  # noqa: F823
            except NameError:
                # In python2 we need to define this built-in, but must ignore it on
                # python3's flake8
                FileNotFoundError = OSError  # noqa: F823
            try:
                instance.run()
                raise RuntimeError("sphinx_pyreverse should not call mdkir -p")
            except FileNotFoundError:
                pass  # aok
            self.assertFalse(os.path.exists(mock_dir))
            os.mkdir(mock_dir)
            try:
                instance.run()
            except FileNotFoundError:
                raise RuntimeError(
                    "sphinx_pyreverse should have created a single directory"
                )
            self.assertTrue(os.path.exists(mock_dir))

    def test_generate_same_twice(self):
        """ check that there are no side-effects of processing the same module twice """
        instance = self.gen()
        instance.run()
        instance.run()
        # TODO: extend the subprocess mock so we can interegate how many times pyreverse
        # was called (should only be once)

    def test_invalid_flags(self):
        """ test graceful handling & reporting of errors in parameters """
        instance = self.gen()
        instance.arguments = ["module_name", ":bad_arg:"]
        try:
            instance.run()
        except ValueError as exception:
            self.assertTrue("invalid flags encountered" in str(exception))

    def test_valid_flags(self):
        """ ensure we accept the currently know valid-flags for pyreverse """
        instance = self.gen()
        for args in ((":classes:", ":packages:"), (":classes:",), (":packages:",)):
            instance.arguments = ["module_name"] + list(args)
            instance.run()

    def test_generate_img(self):
        """ cause UMLGenerateDirective.run() to call generate_image for all branches """
        instance = self.gen()

        def scoped_test(width_under_test):
            def open_too_wide_image(_):
                class MockImage:
                    """ Mocks an image with size params """

                    def __init__(self):
                        self.size = [width_under_test, 0]

                return MockImage()

            test.mock_pil.PIL_MOCK.Image.open = open_too_wide_image  # noqa
            actual_width = test.mock_pil.PIL_MOCK.Image.open("noexist").size[0]
            self.assertEqual(actual_width, width_under_test)
            instance.run()

        for width_under_test in (0, 1, 2000):
            scoped_test(width_under_test)

    def test_generate_img_no_pil(self):
        """ ensure we handle not have the PIL library gracefully

        The intent is to resize too-wide files """
        instance = self.gen()
        old_image = sphinx_pyreverse.uml_generate_directive.IMAGE
        sphinx_pyreverse.uml_generate_directive.IMAGE = None
        instance.run()
        sphinx_pyreverse.uml_generate_directive.IMAGE = old_image

    def test_setup(self):
        """ simply calls the setup function, ensuring no errors """
        self.assertEqual(sphinx_pyreverse.setup(Mock()), None)
