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
import test.mock_PIL
import sphinx_pyreverse

from mock import Mock


class TempdirGuard(object):
    """ creates and deletes a tmp-dir compatible with python2 and 3 """
    def __init__(self):
        self.path = tempfile.mkdtemp(prefix="sphinx_pyreverse_test")

    def __enter__(self):
        return self

    def __exit__(self, x_type, x_value, x_traceback):
        shutil.rmtree(self.path)  # always clean up on exit


class TestUMLGenerateDirective(unittest.TestCase):
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
                instance.run()
                self.assertTrue(False, "sphinx_pyreverse should not call mdkir -p")
            except FileNotFoundError:
                pass  # aok
            self.assertFalse(os.path.exists(mock_dir))
            self.assertFalse(os.path.exists(instance.uml_dir))
            os.mkdir(mock_dir)
            try:
                instance.run()
            except FileNotFoundError:
                self.assertFalse(
                    False, "sphinx_pyreverse should have created a single directory"
                )
                raise
            self.assertTrue(os.path.exists(mock_dir))
            self.assertTrue(os.path.exists(instance.uml_dir))

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
        except ValueError as e:
            self.assertTrue("invalid flags encountered" in str(e))

    def test_valid_flags(self):
        """ ensure we accept the currently know valid-flags for pyreverse """
        instance = self.gen()
        for args in ((":classes:", ":packages:"), (":classes:",), (":packages:",)):
            instance.arguments = ["module_name"] + list(args)
            instance.run()

    def test_generate_img(self):
        """ cause UMLGenerateDirective.run() to call generate_image for all branches """
        instance = self.gen()
        for width_under_test in (0, 1, 2000):

            def open_too_wide_image(path):
                class MockImage:
                    def __init__(self):
                        self.size = [width_under_test, 0]

                return MockImage()

            test.mock_PIL.PIL_MOCK.Image.open = open_too_wide_image
            actual_width = test.mock_PIL.PIL_MOCK.Image.open("noexist").size[0]
            self.assertEqual(actual_width, width_under_test)
            instance.run()

    def test_generate_img_no_PIL(self):
        """ ensure we handle not have the PIL library gracefully

        The intent is to resize too-wide files """
        instance = self.gen()
        oldImage = sphinx_pyreverse.IMAGE
        sphinx_pyreverse.IMAGE = None
        instance.run()
        sphinx_pyreverse.IMAGE = oldImage

    def test_setup(self):
        """ simply calls the setup function, ensuring no errors """
        self.assertEqual(sphinx_pyreverse.setup(Mock()), None)
