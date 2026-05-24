"""Core diffing logic for environment variable sets."""

from dataclasses import dataclass, field
from typing import Dict, Set


@dataclass
class DiffResult:
    added: Dict[str, str] = field(default_factory=dict)
    removed: Dict[str, str] = field(default_factory=dict)
    changed: Dict[str, tuple] = field(default_factory=dict)
    unchanged: Dict[str, str] = field(default_factory=dict)

    def counts(self) -> Dict[str, int]:
        """Return a dictionary of counts for each diff category."""
        return {
            "added": len(self.added),
            "removed": len(self.removed),
            "changed": len(self.changed),
            "unchanged": len(self.unchanged),
        }


def has_differences(result: DiffResult) -> bool:
    """Return True if the diff result contains any differences."""
    return bool(result.added or result.removed or result.changed)


def summary(result: DiffResult) -> str:
    """Return a one-line human-readable summary of the diff."""
    parts = []
    if result.added:
        parts.append(f"{len(result.added)} added")
    if result.removed:
        parts.append(f"{len(result.removed)} removed")
    if result.changed:
        parts.append(f"{len(result.changed)} changed")
    if not parts:
        return "No differences found."
    return ", ".join(parts) + "."


def diff_envs(
    base: Dict[str, str],
    target: Dict[str, str],
    mask: bool = False,
    mask_patterns=None,
    show_length: bool = False,
) -> DiffResult:
    """Diff two environment variable dictionaries.

    Args:
        base: The baseline environment (e.g. production).
        target: The target environment (e.g. staging).
        mask: Whether to mask sensitive values before diffing.
        mask_patterns: Custom patterns for masking (uses defaults if None).
        show_length: When masking, include the original value length.

    Returns:
        A DiffResult describing the differences.
    """
    if mask:
        from envoy_diff.masker import mask_env
        base = mask_env(base, patterns=mask_patterns, show_length=show_length)
        target = mask_env(target, patterns=mask_patterns, show_length=show_length)

    base_keys: Set[str] = set(base.keys())
    target_keys: Set[str] = set(target.keys())

    added = {k: target[k] for k in target_keys - base_keys}
    removed = {k: base[k] for k in base_keys - target_keys}
    changed = {
        k: (base[k], target[k])
        for k in base_keys & target_keys
        if base[k] != target[k]
    }
    unchanged = {
        k: base[k]
        for k in base_keys & target_keys
        if base[k] == target[k]
    }

    return DiffResult(
        added=added,
        removed=removed,
        changed=changed,
        unchanged=unchanged,
    )
