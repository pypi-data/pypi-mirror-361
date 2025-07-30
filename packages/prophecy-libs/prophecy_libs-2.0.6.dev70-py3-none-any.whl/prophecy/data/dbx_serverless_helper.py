"""
Databricks Serverless Helper utilities.

This module provides utilities to access the Databricks serverless requirements file
that is bundled with the prophecy-libs package.
"""

import sys
from importlib import resources
from pathlib import Path


REQUIREMENTS_FILE = "requirements.dbxserverless_sandbox.txt"


def _get_requirements_content() -> str:
    """
    Get the content of the serverless requirements file.
    
    Returns:
        str: The content of the requirements file
        
    Raises:
        FileNotFoundError: If the requirements file cannot be found
    """
    try:
        # Python 3.9+
        with resources.files("prophecy.data").joinpath(REQUIREMENTS_FILE).open() as f:
            return f.read()
    except AttributeError:
        # Python 3.8 fallback
        with resources.open_text("prophecy.data", REQUIREMENTS_FILE) as f:
            return f.read()


def print_serverless_requirements() -> None:
    """Print the contents of the serverless requirements file to stdout."""
    content = _get_requirements_content()
    print(content, end="")


def write_serverless_requirements(output_path: str) -> None:
    """
    Write the serverless requirements to a file.
    
    Args:
        output_path: Path where the requirements file should be written
        
    Raises:
        OSError: If the file cannot be written
    """
    content = _get_requirements_content()
    
    # Ensure parent directory exists
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        f.write(content)


def get_serverless_requirements_path() -> str:
    """
    Get the file path to the serverless requirements file.
    
    Returns:
        str: Absolute path to the requirements file
        
    Note:
        This returns a temporary path that may not persist across Python sessions.
        Use write_serverless_requirements() to create a persistent copy.
    """
    try:
        # Python 3.9+
        files = resources.files("prophecy.data")
        req_file = files.joinpath(REQUIREMENTS_FILE)
        with resources.as_file(req_file) as path:
            return str(path)
    except AttributeError:
        # Python 3.8 fallback
        import pkg_resources
        return pkg_resources.resource_filename("prophecy.data", REQUIREMENTS_FILE)


def main() -> None:
    """
    Main CLI entry point.
    
    Usage:
        python -m prophecy.utils.dbx_serverless_helper                 # Print to stdout
        python -m prophecy.utils.dbx_serverless_helper <output_file>   # Write to file
    """
    if len(sys.argv) == 1:
        # No arguments: print to stdout
        print_serverless_requirements()
        
    elif len(sys.argv) == 2:
        # One argument: write to specified file
        output_path = sys.argv[1]
        try:
            write_serverless_requirements(output_path)
            print(f"Requirements written to: {output_path}")
        except OSError as e:
            print(f"Error writing to {output_path}: {e}", file=sys.stderr)
            sys.exit(1)
            
    else:
        # Too many arguments
        print("Usage: python -m prophecy.utils.dbx_serverless_helper [output_file]")
        print("  No arguments: print to stdout")
        print("  output_file: write to specified file")
        sys.exit(1)


if __name__ == "__main__":
    main()