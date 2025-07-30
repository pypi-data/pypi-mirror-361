"""
Tests for the CLI module.
"""

from unittest.mock import patch

import pytest

from attnseeker.cli import create_parser, main


class TestCreateParser:
    """Test the create_parser function."""

    def test_create_parser_returns_argument_parser(self):
        """Test that create_parser returns an ArgumentParser."""
        parser = create_parser()
        assert parser is not None
        assert hasattr(parser, "parse_args")

    def test_create_parser_has_expected_arguments(self):
        """Test that the parser has the expected arguments."""
        parser = create_parser()
        args = parser.parse_args([])

        # Check default values
        assert args.name == "World"
        assert args.verbose is False

    def test_create_parser_name_argument(self):
        """Test the name argument."""
        parser = create_parser()
        args = parser.parse_args(["--name", "Alice"])
        assert args.name == "Alice"

    def test_create_parser_verbose_argument(self):
        """Test the verbose argument."""
        parser = create_parser()
        args = parser.parse_args(["--verbose"])
        assert args.verbose is True

    def test_create_parser_verbose_short_argument(self):
        """Test the verbose short argument."""
        parser = create_parser()
        args = parser.parse_args(["-v"])
        assert args.verbose is True


class TestMain:
    """Test the main function."""

    @patch("sys.stdout")
    def test_main_success_default_args(self, mock_stdout):
        """Test main function with default arguments."""
        result = main([])
        assert result == 0

    @patch("sys.stdout")
    def test_main_success_custom_name(self, mock_stdout):
        """Test main function with custom name."""
        result = main(["--name", "Alice"])
        assert result == 0

    @patch("sys.stdout")
    def test_main_success_verbose(self, mock_stdout):
        """Test main function with verbose flag."""
        result = main(["--verbose"])
        assert result == 0

    @patch("sys.stdout")
    def test_main_success_all_options(self, mock_stdout):
        """Test main function with all options."""
        result = main(["--name", "Bob", "--verbose"])
        assert result == 0

    @patch("sys.stderr")
    def test_main_version_argument(self, mock_stderr):
        """Test main function with version argument."""
        with pytest.raises(SystemExit) as exc_info:
            main(["--version"])
        assert exc_info.value.code == 0

    @patch("sys.stderr")
    def test_main_help_argument(self, mock_stderr):
        """Test main function with help argument."""
        with pytest.raises(SystemExit) as exc_info:
            main(["--help"])
        assert exc_info.value.code == 0


class TestCLIIntegration:
    """Integration tests for CLI functionality."""

    @patch("builtins.print")
    def test_cli_output_contains_expected_messages(self, mock_print):
        """Test that CLI output contains expected messages."""
        main([])

        # Check that print was called with expected messages
        calls = mock_print.call_args_list
        assert len(calls) >= 2  # At least main_function and greet calls

        # Check for main function output
        main_output = any("attnseeker" in str(call) for call in calls)
        assert main_output

        # Check for greeting output
        greeting_output = any(
            "Hello, World! I'm seeking attention!" in str(call) for call in calls
        )
        assert greeting_output

    @patch("builtins.print")
    def test_cli_custom_name_output(self, mock_print):
        """Test CLI output with custom name."""
        main(["--name", "Alice"])

        calls = mock_print.call_args_list
        greeting_output = any(
            "Hello, Alice! I'm seeking attention!" in str(call) for call in calls
        )
        assert greeting_output

    @patch("builtins.print")
    def test_cli_verbose_output(self, mock_print):
        """Test CLI verbose output."""
        main(["--verbose"])

        calls = mock_print.call_args_list
        verbose_output = any("Verbose mode enabled" in str(call) for call in calls)
        assert verbose_output
