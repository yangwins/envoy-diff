"""Transform environment variable dicts before diffing.

Supports prefix stripping, key renaming via a mapping, and value
substitution so that two envs with different naming conventions can
still be compared meaningfully.
"""

from __future__ import annotations

from typing import Dict, Optional


EnvDict = Dict[str, str]


def strip_prefix(env: EnvDict, prefix: str) -> EnvDict:
    """Return a new dict with *prefix* removed from every matching key.

    Keys that do not start with *prefix* are kept as-is.
    """
    if not isinstance(env, dict):
        raise TypeError("env must be a dict")
    result: EnvDict = {}
    for key, value in env.items():
        new_key = key[len(prefix):] if key.startswith(prefix) else key
        result[new_key] = value
    return result


def rename_keys(env: EnvDict, mapping: Dict[str, str]) -> EnvDict:
    """Return a new dict with keys renamed according to *mapping*.

    Keys absent from *mapping* are kept unchanged.  If two source keys
    would map to the same target key the last one (in iteration order)
    wins.
    """
    if not isinstance(env, dict):
        raise TypeError("env must be a dict")
    if not isinstance(mapping, dict):
        raise TypeError("mapping must be a dict")
    return {mapping.get(k, k): v for k, v in env.items()}


def substitute_values(env: EnvDict, substitutions: Dict[str, str]) -> EnvDict:
    """Return a new dict where values equal to a key in *substitutions*
    are replaced by the corresponding substitution value.

    Useful for normalising placeholder values like ``'<unset>'`` to
    empty strings before diffing.
    """
    if not isinstance(env, dict):
        raise TypeError("env must be a dict")
    return {k: substitutions.get(v, v) for k, v in env.items()}


def transform_env(
    env: EnvDict,
    *,
    strip_prefix_str: Optional[str] = None,
    key_mapping: Optional[Dict[str, str]] = None,
    value_substitutions: Optional[Dict[str, str]] = None,
) -> EnvDict:
    """Apply a pipeline of transformations to *env* and return the result.

    All parameters are optional; omitting them is a no-op for that step.
    """
    result = dict(env)
    if strip_prefix_str:
        result = strip_prefix(result, strip_prefix_str)
    if key_mapping:
        result = rename_keys(result, key_mapping)
    if value_substitutions:
        result = substitute_values(result, value_substitutions)
    return result
