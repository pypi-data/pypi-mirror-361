"""
Command-line interface for the attnseeker package.
"""

import argparse
import sys
from typing import Optional

from .core import main_function, AttnSeeker


def create_parser() -> argparse.ArgumentParser:
    """
    Create the command-line argument parser.
    
    Returns:
        argparse.ArgumentParser: Configured argument parser
    """
    parser = argparse.ArgumentParser(
        description="AttnSeeker - A Python package for attention-seeking functionality",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  attnseeker                    # Run with default settings
  attnseeker --name "World"     # Run with custom name
  attnseeker --version          # Show version information
        """,
    )
    
    parser.add_argument(
        "--name",
        type=str,
        default="World",
        help="Name to use in greeting (default: World)",
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="attnseeker 0.1.0",
        help="Show version information and exit",
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output",
    )
    
    return parser


def main(args: Optional[list] = None) -> int:
    """
    Main entry point for the command-line interface.
    
    Args:
        args: Command-line arguments (defaults to sys.argv[1:])
        
    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    
    try:
        # Run the main function
        result = main_function()
        print(result)
        
        # Create an instance of AttnSeeker
        instance = AttnSeeker(parsed_args.name)
        greeting = instance.greet()
        print(greeting)
        
        if parsed_args.verbose:
            print("Verbose mode enabled")
            print(f"Arguments: {parsed_args}")
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main()) 