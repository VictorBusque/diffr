"""Command-line interface for diffr."""

import argparse
import sys

from .core import diff_files
from .utils.formatter import format_diff


def main():
    """Run entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Compare files and display differences")
    parser.add_argument("file1", help="First file to compare")
    parser.add_argument("file2", help="Second file to compare")
    parser.add_argument(
        "--format", choices=["unified", "context"], default="unified", help="Output format (default: unified)"
    )

    args = parser.parse_args()

    diff = diff_files(args.file1, args.file2)
    formatted_diff = format_diff(diff, args.format)
    print(formatted_diff)

    return 0


if __name__ == "__main__":
    sys.exit(main())
