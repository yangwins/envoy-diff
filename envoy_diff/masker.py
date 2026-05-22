"""Masking utilities for sensitive environment variable values."""

import re
from typing import Dict, Optional

# Default patterns that indicate a value should be masked
DEFAULT_SENSITIVE_PATTERNS = [
    re.compile(r"secret", re.IGNORECASE),
    re.compile(r"password", re.IGNORECASE),
    re.compile(r"passwd", re.IGNORECASE),
    re.compile(r"token", re.IGNORECASE),
    re.compile(r"api[_\-]?key", re.IGNORECASE),
    re.compile(r"private[_\-]?key", re.IGNORECASE),
    re.compile(r"auth", re.IGNORECASE),
    re.compile(r"credential", re.IGNORECASE),
]

MASK_VALUE = "***"


def is_sensitive(key: str, patterns: Optional[list] = None) -> bool:
    """Return True if the key matches any sensitive pattern."""
    if patterns is None:
        patterns = DEFAULT_SENSITIVE_PATTERNS
    return any(pattern.search(key) for pattern in patterns)


def mask_value(value: str, show_length: bool = False) -> str:
    """Return a masked representation of a sensitive value."""
    if show_length:
        return f"{MASK_VALUE}({len(value)})"
    return MASK_VALUE


def mask_env(
    env: Dict[str, str],
    patterns: Optional[list] = None,
    show_length: bool = False,
) -> Dict[str, str]:
    """Return a copy of env with sensitive values masked."""
    return {
        key: mask_value(value, show_length=show_length)
        if is_sensitive(key, patterns=patterns)
        else value
        for key, value in env.items()
    }
