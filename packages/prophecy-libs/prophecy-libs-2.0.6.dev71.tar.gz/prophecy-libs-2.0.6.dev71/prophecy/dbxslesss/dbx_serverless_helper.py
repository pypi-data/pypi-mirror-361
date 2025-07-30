"""
Databricks Serverless Helper utilities.
"""

from importlib import resources
from pathlib import Path


def print_serverless_requirements(output_path: str) -> None:
    """
    Write the serverless requirements to a file.
    
    Args:
        output_path: Path where the requirements file should be written
    """
    try:
        # Python 3.9+
        with resources.files("prophecy.data").joinpath("requirements.dbxserverless_sandbox.txt").open() as f:
            content = f.read()
    except AttributeError:
        # Python 3.8 fallback
        with resources.open_text("prophecy.data", "requirements.dbxserverless_sandbox.txt") as f:
            content = f.read()
    
    # Ensure parent directory exists
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        f.write(content)