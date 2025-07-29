"""
Dynamic function model generation.
"""

import inspect
from typing import Any, Callable, Type
from pydantic import BaseModel, Field, create_model

from .utils import (
    parse_docstring_params,
    clean_annotation_string,
    get_docstring_summary,
    get_docstring_description,
)


def create_function_model(func: Callable) -> Type[BaseModel]:
    """
    Create a Pydantic model dynamically from function signature.

    Args:
        func: Function to analyze

    Returns:
        Pydantic model class for the function parameters
    """
    sig = inspect.signature(func)
    fields = {}

    # Parse docstring for parameter descriptions
    param_descriptions = parse_docstring_params(func.__doc__ or "")

    for param_name, param in sig.parameters.items():
        # Skip self/cls parameters
        if param_name in ("self", "cls"):
            continue

        # Get parameter description from docstring
        description = param_descriptions.get(param_name)

        # Set default value
        if param.default is param.empty:
            default = ...
        else:
            default = param.default

        # Create field with annotation and metadata
        fields[param_name] = (
            param.annotation if param.annotation is not param.empty else Any,
            Field(default=default, description=description),
        )

    # Create model dynamically
    return create_model(f"{func.__name__}Model", **fields)


def analyze_function(func: Callable) -> dict:
    """
    Analyze function and return metadata.

    Args:
        func: Function to analyze

    Returns:
        Dictionary with function metadata
    """
    sig = inspect.signature(func)

    # Parse docstring for parameter descriptions
    param_descriptions = parse_docstring_params(func.__doc__ or "")

    # Extract summary and description
    summary = get_docstring_summary(func.__doc__ or "")
    description = get_docstring_description(func.__doc__ or "")

    return {
        "name": func.__name__,
        "module": func.__module__,
        "docstring": func.__doc__,
        "summary": summary,  # Brief one-line description
        "description": description,  # Detailed description
        "is_async": inspect.iscoroutinefunction(func),
        "is_generator": inspect.isgeneratorfunction(func),
        "return_annotation": clean_annotation_string(sig.return_annotation),
        "parameters": [
            {
                "name": name,
                "annotation": clean_annotation_string(param.annotation),
                "default": param.default if param.default is not param.empty else None,
                "kind": str(param.kind),
                "description": param_descriptions.get(name),
            }
            for name, param in sig.parameters.items()
            if name not in ("self", "cls")
        ],
    }
