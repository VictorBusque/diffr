try:
    from .myers import diff_line, tokenize
    from .patience import diff_code, diff_hunks
except ImportError:
    # Fallback for when Cython modules are not compiled
    # This helps during development or when installing in editable mode
    import warnings

    warnings.warn("Cython modules not available, falling back to pure Python implementations")

__all__ = ["diff_line", "diff_code", "diff_hunks", "tokenize"]
