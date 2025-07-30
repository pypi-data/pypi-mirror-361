"""
Databricks Serverless Helper utilities.
"""

import sys
from importlib import resources


def print_serverless_requirements():
    """Print the contents of the serverless requirements file to stdout"""
    try:
        # Python 3.9+
        with resources.files("prophecy.data").joinpath("requirements.dbxserverless_sandbox.txt").open() as f:
            print(f.read(), end="")
    except AttributeError:
        # Python 3.8 fallback
        with resources.open_text("prophecy.data", "requirements.dbxserverless_sandbox.txt") as f:
            print(f.read(), end="")


def get_serverless_requirements_path():
    """Get the file path to the serverless requirements file"""
    try:
        # Python 3.9+
        files = resources.files("prophecy.data")
        req_file = files.joinpath("requirements.dbxserverless_sandbox.txt")
        with resources.as_file(req_file) as path:
            return str(path)
    except AttributeError:
        # Python 3.8 fallback
        import pkg_resources
        return pkg_resources.resource_filename("prophecy.data", "requirements.dbxserverless_sandbox.txt")


def main():
    """Main CLI entry point"""
    if len(sys.argv) == 1:
        # Default behavior: print requirements
        print_serverless_requirements()
    elif len(sys.argv) == 2:
        command = sys.argv[1]
        if command == "print":
            print_serverless_requirements()
        elif command == "path":
            print(get_serverless_requirements_path())
        else:
            print(f"Unknown command: {command}")
            print("Usage: python -m prophecy.utils.dbx_serverless_helper [print|path]")
            sys.exit(1)
    else:
        print("Usage: python -m prophecy.utils.dbx_serverless_helper [print|path]")
        sys.exit(1)


if __name__ == "__main__":
    main()