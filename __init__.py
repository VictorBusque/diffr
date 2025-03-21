"""diffr - A Python package for generating and working with diffs."""

__version__ = "0.1.0"

# Import and expose key functionality
from .core import diff_files

# Provide convenient imports for users
from .utils.formatter import format_diff

__all__ = ["diff_files", "format_diff"]
