"""Compute statistical metrics over a DiffResult for reporting and scoring."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envoy_diff.differ import DiffResult


@dataclass
class DiffStats:
    """Aggregated statistics derived from a DiffResult."""

    total_keys: int
    added: int
    removed: int
    changed: int
    unchanged: int
    change_rate: float  # fraction of total_keys that changed (added+removed+changed)
    top_changed_keys: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict:
        return {
            "total_keys": self.total_keys,
            "added": self.added,
            "removed": self.removed,
            "changed": self.changed,
            "unchanged": self.unchanged,
            "change_rate": round(self.change_rate, 4),
            "top_changed_keys": self.top_changed_keys,
        }


def compute_stats(
    result: DiffResult,
    top_n: int = 5,
) -> DiffStats:
    """Return a DiffStats summary for *result*.

    Parameters
    ----------
    result:
        The diff result to analyse.
    top_n:
        How many changed/added/removed keys to include in *top_changed_keys*
        (sorted alphabetically).
    """
    added = len(result.added)
    removed = len(result.removed)
    changed = len(result.changed)
    unchanged = len(result.unchanged)
    total = added + removed + changed + unchanged

    change_rate = (added + removed + changed) / total if total > 0 else 0.0

    # Collect all "interesting" keys and sort them for determinism
    interesting: List[str] = sorted(
        list(result.added.keys())
        + list(result.removed.keys())
        + list(result.changed.keys())
    )
    top_changed_keys = interesting[:top_n]

    return DiffStats(
        total_keys=total,
        added=added,
        removed=removed,
        changed=changed,
        unchanged=unchanged,
        change_rate=change_rate,
        top_changed_keys=top_changed_keys,
    )


def format_stats(stats: DiffStats) -> str:
    """Return a human-readable summary string for *stats*."""
    lines = [
        f"Total keys : {stats.total_keys}",
        f"Added      : {stats.added}",
        f"Removed    : {stats.removed}",
        f"Changed    : {stats.changed}",
        f"Unchanged  : {stats.unchanged}",
        f"Change rate: {stats.change_rate:.1%}",
    ]
    if stats.top_changed_keys:
        keys_str = ", ".join(stats.top_changed_keys)
        lines.append(f"Top keys   : {keys_str}")
    return "\n".join(lines)
