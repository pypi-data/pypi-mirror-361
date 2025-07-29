"""
Multiline String Indentation Fixer

A tool that automatically fixes multiline string indentation in Python files.
"""

__version__ = '1.0.0'
__author__ = 'Martin Kalema'
__description__ = 'Tool for fixing multiline string indentation'

from .presentation.cli import cli

__all__ = ['cli']