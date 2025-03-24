def diff_line(a: str, b: str) -> list:
    """Pure Python implementation of diff_line function."""
    # A simple implementation that can be used as fallback
    # Consider implementing a simplified version of the Myers algorithm here
    # For now, providing a basic implementation
    result = []
    if a != b:
        result.append(("-", a))
        result.append(("+", b))
    else:
        result.append((" ", a))
    return result


def tokenize(text: str) -> list:
    """Pure Python implementation of tokenize function."""
    # Simple tokenization by space
    return text.split()
