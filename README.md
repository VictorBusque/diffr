# diffr

A Python package for analyzing and visualizing differences between text files.

## Installation

```bash
pip install diffr
```

## Usage

```python
from diffr import diff_code, diff_hunks, diff_line

# Compare two text blocks
result = diff_line("hello world", "hello there")
print(result)

# Compare code with detailed hunks
hunks = diff_hunks("def example():\n    return True", "def example():\n    return False")
print(hunks)
```

## Development

To set up the development environment:

```bash
# Clone the repository
git clone https://github.com/yourusername/diffr.git
cd diffr

# Install in development mode
pip install -e .

# Run tests
pytest
```
