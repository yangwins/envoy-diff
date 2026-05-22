"""Core diffing logic for comparing environment variable sets."""

from dataclasses import dataclass, field
from typing import Dict, Set


@dataclass
class DiffResult:
    """Holds the result of comparing two environment variable sets."""

    added: Dict[str, str] = field(default_factory=dict)
    removed: Dict[str, str] = field(default_factory=dict)
    changed: Dict[str, tuple] = field(default_factory=dict)
    unchanged: Dict[str, str] = field(default_factory=dict)

    @property
    def has_differences(self) -> bool:
        """Return True if there are any differences between the two sets."""
        return bool(self.added or self.removed or self.changed)

    @property
    def summary(self) -> str:
        """Return a human-readable summary of the diff."""
        parts = []
        if self.added:
            parts.append(f"{len(self.added)} added")
        if self.removed:
            parts.append(f"{len(self.removed)} removed")
        if self.changed:
            parts.append(f"{len(self.changed)} changed")
        if not parts:
            return "No differences found."
        return ", ".join(parts) + "."


def diff_envs(
    source: Dict[str, str],
    target: Dict[str, str],
    ignore_keys: Set[str] = None,
) -> DiffResult:
    """Compare two environment variable dictionaries.

    Args:
        source: The baseline environment (e.g. production).
        target: The environment to compare against (e.g. staging).
        ignore_keys: Optional set of keys to exclude from comparison.

    Returns:
        A DiffResult describing the differences.
    """
    if not isinstance(source, dict):
        raise TypeError("source must be a dict")
    if not isinstance(target, dict):
        raise TypeError("target must be a dict")

    ignore_keys = ignore_keys or set()

    source_keys = {k for k in source if k not in ignore_keys}
    target_keys = {k for k in target if k not in ignore_keys}

    added_keys = target_keys - source_keys
    removed_keys = source_keys - target_keys
    common_keys = source_keys & target_keys

    result = DiffResult()

    for key in sorted(added_keys):
        result.added[key] = target[key]

    for key in sorted(removed_keys):
        result.removed[key] = source[key]

    for key in sorted(common_keys):
        if source[key] != target[key]:
            result.changed[key] = (source[key], target[key])
        else:
            result.unchanged[key] = source[key]

    return result
