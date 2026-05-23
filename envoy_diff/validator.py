"""Validator for environment variable sets.

Provides utilities to validate that environment variable dicts conform
to expected shapes: non-empty keys, string values, and optional required
key checks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ValidationResult:
    valid: bool
    errors: List[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.valid


def validate_env(
    env: Dict[str, str],
    *,
    required_keys: Optional[List[str]] = None,
    allow_empty_values: bool = True,
) -> ValidationResult:
    """Validate an environment variable dictionary.

    Args:
        env: The environment dict to validate.
        required_keys: Optional list of keys that must be present.
        allow_empty_values: If False, empty string values are errors.

    Returns:
        A ValidationResult indicating validity and any error messages.
    """
    errors: List[str] = []

    for key, value in env.items():
        if not isinstance(key, str) or not key:
            errors.append(f"Invalid key: {key!r} — keys must be non-empty strings.")
        if not isinstance(value, str):
            errors.append(
                f"Key {key!r} has non-string value: {value!r} (type {type(value).__name__})."
            )
        elif not allow_empty_values and value == "":
            errors.append(f"Key {key!r} has an empty value.")

    if required_keys:
        for rk in required_keys:
            if rk not in env:
                errors.append(f"Required key {rk!r} is missing from the environment.")

    return ValidationResult(valid=len(errors) == 0, errors=errors)


def assert_valid(
    env: Dict[str, str],
    *,
    required_keys: Optional[List[str]] = None,
    allow_empty_values: bool = True,
    label: str = "env",
) -> None:
    """Validate env and raise ValueError with all errors if invalid."""
    result = validate_env(
        env,
        required_keys=required_keys,
        allow_empty_values=allow_empty_values,
    )
    if not result.valid:
        joined = "\n  ".join(result.errors)
        raise ValueError(f"Validation failed for {label!r}:\n  {joined}")
