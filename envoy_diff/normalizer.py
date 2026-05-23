"""Normalize environment variable keys and values for consistent comparison."""

from __future__ import annotations

from typing import Dict


Env = Dict[str, str]


def normalize_keys(env: Env, *, uppercase: bool = True) -> Env:
    """Return a new env with all keys normalized (uppercased by default)."""
    if not isinstance(env, dict):
        raise TypeError(f"Expected dict, got {type(env).__name__}")
    if uppercase:
        return {k.upper(): v for k, v in env.items()}
    return {k.lower(): v for k, v in env.items()}


def normalize_values(env: Env, *, strip: bool = True) -> Env:
    """Return a new env with values stripped of leading/trailing whitespace."""
    if not isinstance(env, dict):
        raise TypeError(f"Expected dict, got {type(env).__name__}")
    if strip:
        return {k: v.strip() for k, v in env.items()}
    return dict(env)


def normalize_env(
    env: Env,
    *,
    uppercase_keys: bool = True,
    strip_values: bool = True,
) -> Env:
    """Apply all normalization steps to an env dict.

    Parameters
    ----------
    env:
        The environment mapping to normalize.
    uppercase_keys:
        When True (default) all keys are converted to upper-case.
    strip_values:
        When True (default) leading/trailing whitespace is removed from values.
    """
    result = normalize_keys(env, uppercase=uppercase_keys)
    result = normalize_values(result, strip=strip_values)
    return result


def deduplicate_keys(env: Env) -> Env:
    """Return env unchanged; documents that dict keys are already unique.

    Raises ValueError if the *original* dict somehow contains duplicate keys
    after case-folding (useful when building an env from a list of pairs).
    """
    seen: set[str] = set()
    for key in env:
        folded = key.upper()
        if folded in seen:
            raise ValueError(f"Duplicate key after normalization: {key!r}")
        seen.add(folded)
    return dict(env)
