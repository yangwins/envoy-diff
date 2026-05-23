"""Merge two environment dicts with configurable conflict resolution strategies."""

from __future__ import annotations

from enum import Enum
from typing import Dict, Optional


class MergeStrategy(str, Enum):
    LEFT = "left"      # left (base) wins on conflict
    RIGHT = "right"    # right (override) wins on conflict
    STRICT = "strict"  # raise on any conflict


class MergeConflictError(Exception):
    """Raised when STRICT strategy encounters a conflicting key."""

    def __init__(self, key: str, left_val: str, right_val: str) -> None:
        self.key = key
        self.left_val = left_val
        self.right_val = right_val
        super().__init__(
            f"Conflict on key {key!r}: {left_val!r} vs {right_val!r}"
        )


def merge_envs(
    left: Dict[str, str],
    right: Dict[str, str],
    strategy: MergeStrategy = MergeStrategy.RIGHT,
    prefix: Optional[str] = None,
) -> Dict[str, str]:
    """Return a new dict that merges *left* and *right*.

    Args:
        left: Base environment dict.
        right: Override environment dict.
        strategy: How to resolve key conflicts (default: right wins).
        prefix: If given, only keys from *right* that start with this
                prefix are considered for merging.

    Returns:
        Merged environment as a plain ``dict[str, str]``.

    Raises:
        MergeConflictError: When *strategy* is STRICT and a key exists
                            in both dicts with different values.
        TypeError: When either argument is not a ``dict``.
    """
    if not isinstance(left, dict) or not isinstance(right, dict):
        raise TypeError("Both left and right must be dicts")

    result: Dict[str, str] = {str(k): str(v) for k, v in left.items()}

    for key, value in right.items():
        key = str(key)
        value = str(value)

        if prefix and not key.startswith(prefix):
            continue

        if key in result and result[key] != value:
            if strategy == MergeStrategy.STRICT:
                raise MergeConflictError(key, result[key], value)
            elif strategy == MergeStrategy.LEFT:
                continue  # keep left value
            else:  # RIGHT
                result[key] = value
        else:
            result[key] = value

    return result


#: Convenience aliases
merge_strategies: list[str] = [s.value for s in MergeStrategy]
