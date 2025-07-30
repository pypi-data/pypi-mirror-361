"""
Tests for the core module.
"""

from attnseeker.core import AttnSeeker, main_function, process_data


class TestMainFunction:
    """Test the main_function."""

    def test_main_function_returns_string(self):
        """Test that main_function returns a string."""
        result = main_function()
        assert isinstance(result, str)
        assert "attnseeker" in result

    def test_main_function_returns_expected_message(self):
        """Test that main_function returns the expected message."""
        result = main_function()
        assert result == "Hello from attnseeker!"


class TestProcessData:
    """Test the process_data function."""

    def test_process_data_returns_dict(self):
        """Test that process_data returns a dictionary."""
        input_data = {"key": "value"}
        result = process_data(input_data)
        assert isinstance(result, dict)

    def test_process_data_adds_processed_flag(self):
        """Test that process_data adds the processed flag."""
        input_data = {"key": "value"}
        result = process_data(input_data)
        assert result["processed"] is True

    def test_process_data_preserves_original_data(self):
        """Test that process_data preserves original data."""
        input_data = {"key": "value", "number": 42}
        result = process_data(input_data)
        assert result["key"] == "value"
        assert result["number"] == 42

    def test_process_data_creates_copy(self):
        """Test that process_data creates a copy, not a reference."""
        input_data = {"key": "value"}
        result = process_data(input_data)
        input_data["key"] = "modified"
        assert result["key"] == "value"  # Should not be modified


class TestAttnSeeker:
    """Test the AttnSeeker class."""

    def test_attnseeker_initialization_default(self):
        """Test AttnSeeker initialization with default name."""
        instance = AttnSeeker()
        assert instance.name == "default"

    def test_attnseeker_initialization_custom(self):
        """Test AttnSeeker initialization with custom name."""
        instance = AttnSeeker("Alice")
        assert instance.name == "Alice"

    def test_attnseeker_greet(self):
        """Test AttnSeeker greet method."""
        instance = AttnSeeker("Bob")
        result = instance.greet()
        assert result == "Hello, Bob! I'm seeking attention!"

    def test_attnseeker_greet_default(self):
        """Test AttnSeeker greet method with default name."""
        instance = AttnSeeker()
        result = instance.greet()
        assert result == "Hello, default! I'm seeking attention!"

    def test_attnseeker_process(self):
        """Test AttnSeeker process method."""
        instance = AttnSeeker("TestClass")
        input_data = {"key": "value"}
        result = instance.process(input_data)

        assert isinstance(result, dict)
        assert result["processed"] is True
        assert result["class_name"] == "TestClass"
        assert result["attention_seeking"] is True
        assert result["key"] == "value"

    def test_attnseeker_process_preserves_data(self):
        """Test that AttnSeeker process method preserves original data."""
        instance = AttnSeeker("TestClass")
        input_data = {"key": "value", "number": 123}
        result = instance.process(input_data)

        assert result["key"] == "value"
        assert result["number"] == 123
