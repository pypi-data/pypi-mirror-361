"""richpyls - A modern, type-annotated Python implementation of the Unix ls command.

This package provides a command-line utility that mimics the behavior of the Unix
ls command, implemented in modern Python with type hints and comprehensive error
handling.
"""

__version__ = "0.1.3"
__author__ = "Leodanis Pozo Ramos"
__email__ = "lpozor78@gmail.com"

# Import the main CLI function from __main__ module
from .__main__ import cli

__all__ = ["cli"]
