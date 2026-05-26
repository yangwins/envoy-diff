"""Redactor: selectively blank out env var values before diffing or reporting.

Unlike the masker (which replaces with asterisks), the redactor removes values
entirely, replacing them with a configurable placeholder such as '<REDACTED>'.
This is useful when you want to share diff output without leaking any hint of
the original value length.
"""

from __future__ import annotations

from typing import Dict, Iterable, Optional

DEFAULT_PLACEHOLDER = "<REDACTED>"


def redact_keys(
    env: Dict[str, str],
    keys: Iterable[str],
    placeholder: str = DEFAULT_PLACEHOLDER,
) -> Dict[str, str]:
    """Return a copy of *env* with specific *keys* replaced by *placeholder*."""
    if not isinstance(env, dict):
        raise TypeError("env must be a dict")
    key_set = set(keys)
    return {k: (placeholder if k in key_set else v) for k, v in env.items()}


def redact_all(
    env: Dict[str, str],
    placeholder: str = DEFAULT_PLACEHOLDER,
) -> Dict[str, str]:
    """Return a copy of *env* with every value replaced by *placeholder*."""
    if not isinstance(env, dict):
        raise TypeError("env must be a dict")
    return {k: placeholder for k in env}


def is_redacted(value: str, placeholder: str = DEFAULT_PLACEHOLDER) -> bool:
    """Return True if *value* is the redaction placeholder."""
    return value == placeholder


def redact_env(
    env: Dict[str, str],
    keys: Optional[Iterable[str]] = None,
    placeholder: str = DEFAULT_PLACEHOLDER,
) -> Dict[str, str]:
    """High-level helper: redact *keys* if provided, otherwise redact all.

    Parameters
    ----------
    env:         Source environment mapping.
    keys:        Iterable of key names to redact.  Pass ``None`` to redact
                 every key.
    placeholder: Replacement string (default ``'<REDACTED>'``).
    """
    if keys is None:
        return redact_all(env, placeholder=placeholder)
    return redact_keys(env, keys, placeholder=placeholder)
