"""
Utility functions for function analysis.
"""

import ast
import re
from typing import Any, Dict, List, Optional
from enum import Enum
from docstring_parser import parse as parse_docstring
from docstring_parser.common import DocstringParam


class DocstringStyle(str, Enum):
    """Supported docstring styles"""

    GOOGLE = "google"
    NUMPY = "numpy"
    SPHINX = "sphinx"
    AUTO = "auto"


class AnnotationCleaner(ast.NodeVisitor):
    """Remove unnecessary module prefixes from annotations using AST"""

    def __init__(self):
        self.result = []

    def visit_Name(self, node):
        """Simple names (e.g., str, int)"""
        self.result.append(node.id)

    def visit_Attribute(self, node):
        """Attribute access (e.g., typing.Optional, __main__.MyClass)"""
        # Use only the last attribute name
        self.result.append(node.attr)

    def visit_Subscript(self, node):
        """Generic types (e.g., Optional[str], List[int])"""
        self.visit(node.value)
        self.result.append("[")

        if isinstance(node.slice, ast.Tuple):
            # Multiple arguments (e.g., Dict[str, int])
            for i, elt in enumerate(node.slice.elts):
                if i > 0:
                    self.result.append(", ")
                self.visit(elt)
        else:
            # Single argument (e.g., Optional[str])
            self.visit(node.slice)

        self.result.append("]")

    def visit_Constant(self, node):
        """Constant values"""
        self.result.append(repr(node.value))

    def visit_BinOp(self, node):
        """Binary operations (e.g., Union represented as |)"""
        self.visit(node.left)
        if isinstance(node.op, ast.BitOr):
            self.result.append(" | ")
        self.visit(node.right)


def clean_annotation_ast(annotation_str: str) -> str:
    """Clean annotation string using AST"""
    try:
        # Parse string as AST
        tree = ast.parse(annotation_str, mode="eval")

        # Apply cleaner
        cleaner = AnnotationCleaner()
        cleaner.visit(tree.body)

        return "".join(cleaner.result)

    except (SyntaxError, ValueError):
        # Fallback to pattern-based cleaning if AST parsing fails
        return clean_annotation_pattern(annotation_str)


def clean_annotation_pattern(annotation_str: str) -> str:
    """Clean annotation string using pattern-based approach"""
    # Patterns to remove module prefixes
    patterns = [
        (r"typing\.", ""),
        (r"__main__\.", ""),
        (r"builtins\.", ""),
        (r"collections\.abc\.", ""),
        (
            r"[a-zA-Z_][a-zA-Z0-9_]*\.([A-Z][a-zA-Z0-9_]*)",
            r"\1",
        ),  # module.Class -> Class
        (r"<class '(\w+)'>", r"\1"),  # <class 'str'> -> str
        (r"<class '(\w+\.\w+)'>", r"\1"),  # <class 'typing.List'> -> typing.List
    ]

    cleaned = annotation_str
    for pattern, replacement in patterns:
        cleaned = re.sub(pattern, replacement, cleaned)

    return cleaned


def format_annotation_with_color(annotation: str, color: str = "cyan") -> str:
    """Format annotation with specified color"""
    return f"<fg={color}>({annotation})</>"


def clean_annotation_string(field_annotation: Any, color: str = None) -> str:
    """Convert field annotation to clean string and optionally apply color"""
    annotation_str = str(field_annotation)

    # Try AST-based cleaning
    try:
        clean_annotation = clean_annotation_ast(annotation_str)
    except Exception:
        # Fallback to pattern-based cleaning
        clean_annotation = clean_annotation_pattern(annotation_str)

    # Apply color if specified
    if color:
        return format_annotation_with_color(clean_annotation, color)
    else:
        return f"{clean_annotation}"


def parse_docstring_params(
    docstring: str, style: DocstringStyle = DocstringStyle.AUTO
) -> Dict[str, str]:
    """
    Parse parameter descriptions from docstring.

    Args:
        docstring: Function docstring
        style: Docstring style to use for parsing

    Returns:
        Dictionary mapping parameter names to descriptions
    """
    if not docstring:
        return {}

    try:
        # Parse docstring
        parsed = parse_docstring(docstring)

        # Extract parameter descriptions
        param_descriptions = {}
        for param in parsed.params:
            if param.description:
                param_descriptions[param.arg_name] = param.description.strip()

        return param_descriptions

    except Exception:
        # Fallback to manual parsing for common patterns
        return _parse_docstring_manual(docstring)


def get_docstring_summary(docstring: str) -> str:
    """
    Extract the summary (first line) from a docstring.

    Args:
        docstring: Function docstring

    Returns:
        The first non-empty line of the docstring, or empty string if none
    """
    if not docstring:
        return ""

    # Split into lines and find the first non-empty line
    lines = docstring.strip().split("\n")
    for line in lines:
        line = line.strip()
        if line:
            return line

    return ""


def get_docstring_description(docstring: str) -> str:
    """
    Extract the full description (everything after the summary) from a docstring.

    Args:
        docstring: Function docstring

    Returns:
        The description part of the docstring
    """
    if not docstring:
        return ""

    lines = docstring.strip().split("\n")

    # Find the first non-empty line (summary)
    summary_index = -1
    for i, line in enumerate(lines):
        if line.strip():
            summary_index = i
            break

    if summary_index == -1:
        return ""

    # Find the start of description (after blank line following summary)
    description_start = summary_index + 1

    # Skip any blank lines after summary
    while description_start < len(lines) and not lines[description_start].strip():
        description_start += 1

    if description_start >= len(lines):
        return ""

    # Extract description until Args/Parameters/Returns section
    description_lines = []
    for line in lines[description_start:]:
        # Stop at common section headers
        if re.match(
            r"^\s*(Args|Arguments|Parameters|Returns|Yields|Raises|Note|Notes|Example|Examples):\s*$",
            line,
        ):
            break
        if re.match(
            r"^\s*(Args|Arguments|Parameters|Returns|Yields|Raises|Note|Notes|Example|Examples)\s*\n?\s*-+",
            "\n".join(lines[description_start:]),
            re.MULTILINE,
        ):
            break
        description_lines.append(line)

    # Remove trailing empty lines
    while description_lines and not description_lines[-1].strip():
        description_lines.pop()

    return "\n".join(description_lines).strip()


def _parse_docstring_manual(docstring: str) -> Dict[str, str]:
    """Manual parsing fallback for common docstring patterns"""
    param_descriptions = {}

    # Google style: :param name: description
    google_pattern = r":param\s+(\w+):\s*(.+?)(?=\n\s*:|\n\s*\n|$)"
    for match in re.finditer(google_pattern, docstring, re.MULTILINE | re.DOTALL):
        param_name = match.group(1)
        description = match.group(2).strip()
        param_descriptions[param_name] = description

    # Sphinx style: :param name: description
    sphinx_pattern = r":param\s+(\w+):\s*(.+?)(?=\n\s*:|\n\s*\n|$)"
    for match in re.finditer(sphinx_pattern, docstring, re.MULTILINE | re.DOTALL):
        param_name = match.group(1)
        description = match.group(2).strip()
        if param_name not in param_descriptions:
            param_descriptions[param_name] = description

    # NumPy style: Parameters\n----------\nname : type\n    description
    numpy_pattern = r"Parameters\n-+\n(.*?)(?=\n\s*\n|\n\s*[A-Z]|\Z)"
    numpy_match = re.search(numpy_pattern, docstring, re.DOTALL)
    if numpy_match:
        params_section = numpy_match.group(1)
        # Parse individual parameters
        param_pattern = r"(\w+)\s*:\s*[^\n]*\n\s*(.+?)(?=\n\s*\w+\s*:|$)"
        for match in re.finditer(param_pattern, params_section, re.DOTALL):
            param_name = match.group(1)
            description = match.group(2).strip()
            if param_name not in param_descriptions:
                param_descriptions[param_name] = description

    return param_descriptions
