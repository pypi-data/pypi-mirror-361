"""
Core functionality for the attnseeker package.
"""

from typing import Any, Dict, Optional


def main_function() -> str:
    """
    Main function of the attnseeker package.

    Returns:
        str: A greeting message
    """
    return "Hello from attnseeker!"


def process_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process input data.

    Args:
        data: Input data dictionary

    Returns:
        Dict[str, Any]: Processed data
    """
    # Add your processing logic here
    processed_data = data.copy()
    processed_data["processed"] = True
    return processed_data


class AttnSeeker:
    """
    Main class for attention-seeking functionality.
    """

    def __init__(self, name: Optional[str] = None):
        """
        Initialize the AttnSeeker.

        Args:
            name: Optional name parameter
        """
        self.name = name or "default"

    def greet(self) -> str:
        """
        Return a greeting message.

        Returns:
            str: Greeting message
        """
        return f"Hello, {self.name}! I'm seeking attention!"

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process data using this AttnSeeker instance.

        Args:
            data: Input data

        Returns:
            Dict[str, Any]: Processed data with class context
        """
        result = process_data(data)
        result["class_name"] = self.name
        result["attention_seeking"] = True
        return result
