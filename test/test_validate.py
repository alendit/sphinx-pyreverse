"""
Defines tests and mock to test the sphinx pyreverse tool

Created on Oct 8, 2019

@author: doublethefish
"""
import logging
import os
import subprocess
import sys
import test.mock_pil
from io import StringIO
from test.sphinx_test_util import MockState
from unittest import mock

import pytest

import sphinx_pyreverse
import sphinx_pyreverse.uml_generate_directive


class CaptureLogger:
    """Context manager to capture `logging` streams

    Args:
        - logger: 'logging` logger object
        - string_buff: StringIO object to put the log output to

    Results:
        The captured output is available via the object passed in as string_buf

    """

    def __init__(self, logger, string_buf):
        self.logger = logger
        self.string_buf = string_buf
        self.handler = logging.StreamHandler(self.string_buf)
        self.old_handlers = []
        self.old_level = None

    def __enter__(self):
        self.logger.level = logging.DEBUG
        self.logger.handlers = []
        self.logger.addHandler(self.handler)
        self.old_handlers = self.logger.handlers
        self.old_level = self.logger.level
        return self

    def __exit__(self, *exc):
        self.logger.removeHandler(self.handler)
        self.logger.handlers = self.old_handlers
        self.logger.level = self.old_level


class TestUMLGenerateDirectiveBase:
    """A collection of tests for the UMLGenerateDirective object"""

    @pytest.fixture(autouse=True)
    def reset_state(self):
        sphinx_pyreverse.UMLGenerateDirective.generated_modules = []

    @pytest.fixture(autouse=True)
    def mocksub(self):
        with mock.patch.object(
            sphinx_pyreverse.uml_generate_directive, "subproc_wrapper"
        ) as mocksub:
            yield mocksub

    def gen(self):
        """Constructs and returns a mocked UMLGenerateDirectiver instance"""

        state = MockState()

        return sphinx_pyreverse.UMLGenerateDirective(
            name="test",
            arguments=["noexist_module", ":classes:", ":packages:"],
            options=None,
            content=None,
            lineno=None,
            content_offset=None,
            block_text=None,
            state=state,
            state_machine=None,
        )


class TestUMLGenerateDirective(TestUMLGenerateDirectiveBase):
    """A collection of tests for the UMLGenerateDirective object"""

    def test_ctor(self):
        """simply constructs a UMLGenerateDirectiver instance with mock values"""
        instance = self.gen()
        assert instance is not None

    def test_run(self, mocksub):
        """simply invokes run with the default setup parameters"""
        instance = self.gen()
        assert not instance.generated_modules
        with mock.patch.dict(
            os.environ, {"TEST ENV VARIABLE": "test value"}, clear=True
        ):
            instance.run()
        assert mocksub.call_count == 1
        called_with = mocksub.call_args_list
        assert called_with[0][0][0] == [
            "pyreverse",
            "--output",
            "png",
            "--project",
            "noexist_module",
            "noexist_module",
        ], "have the default args for pyreverse changed?"

        # check that the env is modified so the pyreverse step is able to find
        # the module it want to diagram
        keyword_args = called_with[0][1]
        assert (
            "TEST ENV VARIABLE" in keyword_args["env"]
        ), "We expect the env to be preserved"
        assert (
            "PYTHONPATH" in keyword_args["env"]
        ), "We expect PYTHONPATH to have been added"
        assert keyword_args["env"] == {
            "PYTHONPATH": ":".join(sys.path),
            "TEST ENV VARIABLE": "test value",
        }

    def test_run_with_pythonpath_set(self, mocksub):
        """invokes run with the env var PYTHONPATH set"""
        instance = self.gen()
        with mock.patch.dict(
            os.environ,
            {"TEST ENV VARIABLE": "test value", "PYTHONPATH": "test path"},
            clear=True,
        ):
            instance.run()
        assert mocksub.call_count == 1
        called_with = mocksub.call_args_list
        assert called_with[0][0][0] == [
            "pyreverse",
            "--output",
            "png",
            "--project",
            "noexist_module",
            "noexist_module",
        ], "have the default args for pyreverse changed?"

        # check that the env is NOT modified so the pyreverse step is able to find
        # the module it want to diagram
        keyword_args = called_with[0][1]
        assert (
            "PYTHONPATH" in keyword_args["env"]
        ), "We expect also expect PYTHONPATH to have been preserved"
        assert keyword_args["env"] == {
            "PYTHONPATH": "test path",
            "TEST ENV VARIABLE": "test value",
        }
        assert (
            "TEST ENV VARIABLE" in keyword_args["env"]
        ), "We expect the env to be preserved"

    def test_uml_dir_creation(self, tmpdir):
        """test that the uml directory is created under the right circumstances

        This just captures current behaviour - there should be no problem changing it.
        """
        try:
            FileNotFoundError  # noqa: F823
        except NameError:
            # In python2 we need to define this built-in, but must ignore it on
            # python3's flake8
            FileNotFoundError = (  # noqa: F823,E501 pylint: disable=redefined-builtin,invalid-name
                OSError
            )
        instance = self.gen()
        mock_dir = tmpdir / "noexist.dir"
        instance.state.document.settings.env.srcdir = mock_dir

        # Check that sphinx_pyreverse doesn't create all the directories.
        with pytest.raises(FileNotFoundError):
            instance.run()
        assert tmpdir.exists()
        assert not mock_dir.exists()

        assert not os.path.exists(mock_dir)

        # Now make the parent dir, sphinx_pyreverse should create everything below
        # that, to a single depth
        os.mkdir(mock_dir)
        try:
            instance.run()
        except FileNotFoundError as err:  # pragma: no cover
            raise RuntimeError(
                "sphinx_pyreverse should have created a single directory"
            ) from err
        assert os.path.exists(mock_dir)

    def test_generate_same_twice(self):
        """check that there are no side-effects of processing the same module twice"""
        instance = self.gen()
        instance.run()
        instance.run()
        # TODO: extend the subprocess mock so we can interegate how many times pyreverse
        # was called (should only be once)

    def test_invalid_flags(self):
        """test graceful handling & reporting of errors in parameters"""
        instance = self.gen()
        instance.arguments = ["module_name", ":bad_arg:"]
        try:
            instance.run()
        except ValueError as exception:
            assert "invalid flags encountered" in str(exception)

    def test_valid_flags(self):
        """ensure we accept the currently know valid-flags for pyreverse"""
        instance = self.gen()
        for args in ((":classes:", ":packages:"), (":classes:",), (":packages:",)):
            instance.arguments = ["module_name"] + list(args)
            with mock.patch(
                "subprocess.check_output",
            ):
                instance.run()

    def test_generate_img(self):
        """cause UMLGenerateDirective.run() to call generate_image for all branches"""
        instance = self.gen()

        for width_under_test, expected_scale in ((0, 100), (1, 100), (2000, 50)):
            with test.mock_pil.DimsUnderTestGuard(width=width_under_test), mock.patch(
                "subprocess.check_output",
            ):
                mock_module = test.mock_pil.PIL_MOCK.Image  # pylint: disable=no-member
                actual_width = mock_module.open("noexist").size[0]
                assert actual_width == width_under_test
                res = instance.run()
                assert res[0]["scale"] == expected_scale, (
                    "Failed for %d" % width_under_test
                )

    def test_generate_img_no_pil(self):
        """ensure we handle not have the PIL library gracefully

        The intent is to resize too-wide files"""
        instance = self.gen()
        old_image = sphinx_pyreverse.uml_generate_directive.IMAGE
        sphinx_pyreverse.uml_generate_directive.IMAGE = None
        instance.run()
        sphinx_pyreverse.uml_generate_directive.IMAGE = old_image

    def test_setup(self):
        """simply calls the setup function, ensuring no errors"""
        assert sphinx_pyreverse.setup(mock.Mock()) == {"parallel_read_safe": True}

    def test_non_default_options(self):
        """Simply calls run with non-default pyreverse options

        The intent here is to get 100% coverage and not test the functionality of
        pyreverse itself, we trust that that is working as per contract"""
        state = MockState()
        config = state.document.settings.env.config

        instance = self.gen()

        assert config.sphinx_pyreverse_output == "png"
        assert config.sphinx_pyreverse_filter_mode is None
        assert config.sphinx_pyreverse_class is None
        assert config.sphinx_pyreverse_show_ancestors is None
        assert config.sphinx_pyreverse_all_ancestors is None
        assert config.sphinx_pyreverse_show_associated is None
        assert config.sphinx_pyreverse_all_associated is None
        assert config.sphinx_pyreverse_show_builtin is None
        assert config.sphinx_pyreverse_module_names is None
        assert config.sphinx_pyreverse_only_classnames is None
        assert config.sphinx_pyreverse_ignore is None

        # Set the config to non-default values
        config.sphinx_pyreverse_output = "dot"
        config.sphinx_pyreverse_filter_mode = "ALL"
        config.sphinx_pyreverse_class = "invalid-class"
        config.sphinx_pyreverse_show_ancestors = "invalid-class"
        config.sphinx_pyreverse_all_ancestors = True
        config.sphinx_pyreverse_show_associated = 100
        config.sphinx_pyreverse_all_associated = True
        config.sphinx_pyreverse_show_builtin = True
        config.sphinx_pyreverse_module_names = "y"
        config.sphinx_pyreverse_ignore = "noexist.py,secondnoeexist.py"

        assert config.sphinx_pyreverse_output == "dot"
        assert config.sphinx_pyreverse_filter_mode == "ALL"
        assert config.sphinx_pyreverse_class == "invalid-class"
        assert config.sphinx_pyreverse_show_ancestors == "invalid-class"
        assert config.sphinx_pyreverse_all_ancestors
        assert config.sphinx_pyreverse_show_associated == 100
        assert config.sphinx_pyreverse_all_associated
        assert config.sphinx_pyreverse_show_builtin
        assert config.sphinx_pyreverse_module_names == "y"
        assert config.sphinx_pyreverse_ignore == "noexist.py,secondnoeexist.py"

        instance._build_command(  # pylint: disable=protected-access
            "test_module", config=config
        )

        # disables --filter option, so run separately
        config.sphinx_pyreverse_only_classnames = True
        assert config.sphinx_pyreverse_only_classnames
        instance._build_command(  # pylint: disable=protected-access
            "test_module", config=config
        )


class TestLogFixture(TestUMLGenerateDirectiveBase):
    """Test logging related aspects of the plugin by capturing output"""

    def test_pyreverse_fails(self):
        """Test that we get output logging when the pyreverse fails"""
        instance = self.gen()

        buf = StringIO()
        with mock.patch.object(
            sphinx_pyreverse.uml_generate_directive,
            "subproc_wrapper",
            side_effect=subprocess.CalledProcessError(returncode=999, cmd="test cmd"),
        ), CaptureLogger(logging.getLogger(), buf):
            with pytest.raises(subprocess.CalledProcessError):
                instance.run()

        # nothing should be printed to stdout or the logger
        assert buf.getvalue() == ""
