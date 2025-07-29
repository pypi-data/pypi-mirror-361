---
version: 0.1.0
---

# Func Analyzer

A Python library for dynamic function analysis, schema generation, and CLI integration.

## Features

- **Dynamic Pydantic Model Generation**: Automatically create Pydantic models from function signatures
- **Intelligent Annotation Cleaning**: Convert complex type annotations to clean, readable strings
- **Docstring Parsing**: Extract parameter descriptions from Google, NumPy, and Sphinx docstring styles
- **CLI-Ready Metadata**: Generate comprehensive function metadata for CLI auto-generation
- **Schema Generation**: Create JSON schemas from function signatures with descriptions

## Installation

```bash
# From local development
pip install -e .

# Or clone and install
git clone https://github.com/crimson206/func-analyzer
cd func-analyzer
pip install -e .
```

## Quick Start

### Basic Function Analysis

```python
from func_analyzer import analyze_function

def sample_user_info(name: str, age: int, email: str = None, active: bool = True) -> dict:
    """
    Create user information dictionary.
    
    Args:
        name: User's full name
        age: User's age in years
        email: User's email address (optional)
        active: Whether user account is active
        
    Returns:
        Dictionary containing user information
    """
    return {"name": name, "age": age, "email": email, "active": active}

# Analyze function
info = analyze_function(sample_user_info)
print(info)
```

### Dynamic Model Generation

```python
from func_analyzer import create_function_model

# Create Pydantic model from function
UserModel = create_function_model(sample_user_info)

# Use the model
user_data = UserModel(name="John Doe", age=30, email="john@example.com")
print(user_data.model_dump())
```

### Annotation Cleaning

```python
from func_analyzer import clean_annotation_string

# Clean complex annotations
annotations = [
    "typing.List[str]",
    "typing.Optional[typing.Dict[str, typing.Any]]",
    "<class 'str'>",
    "Union[str, int, float]"
]

for annotation in annotations:
    cleaned = clean_annotation_string(annotation)
    print(f"{annotation} -> {cleaned}")
```

## Core Components

### Function Analysis

The `analyze_function()` function extracts comprehensive metadata:

- Function name and module
- Parameter information (name, type, default, description)
- Return type annotation
- Docstring content
- Async/generator status

### Dynamic Model Creation

`create_function_model()` generates Pydantic models with:

- Type annotations from function signature
- Parameter descriptions from docstrings
- Default values
- Field validation

### Annotation Cleaning

`clean_annotation_string()` handles:

- `typing.` prefix removal
- `<class 'type'>` string conversion
- Complex nested type simplification
- Union type formatting

## Examples

See the `examples/` directory for comprehensive usage examples:

- `example_basic_analysis.py` - Basic function analysis
- `example_annotation_cleaning.py` - Annotation cleaning with tests
- `example_docstring_parsing.py` - Docstring parsing examples

## CLI Integration

The extracted metadata is designed for CLI auto-generation:

```python
# Example CLI generation data
{
    'name': 'sample_user_info',
    'parameters': [
        {
            'name': 'name',
            'annotation': 'str',
            'description': "User's full name",
            'default': None
        },
        {
            'name': 'age', 
            'annotation': 'int',
            'description': "User's age in years",
            'default': None
        }
    ]
}
```

## Development

### Running Examples

```bash
# Run all examples
cd examples
python example_basic_analysis.py
python example_annotation_cleaning.py
```

### Testing

```bash
# Run tests
python -m pytest tests/
```

## License

MIT License