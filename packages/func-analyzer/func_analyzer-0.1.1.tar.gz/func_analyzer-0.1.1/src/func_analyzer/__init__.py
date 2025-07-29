"""
Function Analyzer Module

A module for dynamically creating Pydantic models from Python functions.
"""

from .analyzer import create_function_model, analyze_function
from .utils import clean_annotation_string, DocstringStyle

__version__ = "0.1.0"
__all__ = [
    "create_function_model",
    "analyze_function",
    "clean_annotation_string",
    "DocstringStyle",
]
