"""Summarizer: produce a concise statistical summary of a DiffResult."""

from dataclasses import dataclass
from typing import Dict

from envoy_diff.differ import DiffResult


@dataclass
class DiffSummary:
    """Counts of each change category plus a human-readable headline."""

    added: int
    removed: int
    changed: int
    unchanged: int
    total: int

    @property
    def headline(self) -> str:
        parts = []
        if self.added:
            parts.append(f"{self.added} added")
        if self.removed:
            parts.append(f"{self.removed} removed")
        if self.changed:
            parts.append(f"{self.changed} changed")
        if not parts:
            return "Environments are identical"
        return ", ".join(parts)

    def as_dict(self) -> Dict[str, int]:
        return {
            "added": self.added,
            "removed": self.removed,
            "changed": self.changed,
            "unchanged": self.unchanged,
            "total": self.total,
        }


def summarize(result: DiffResult) -> DiffSummary:
    """Return a DiffSummary computed from *result*."""
    added = len(result.added)
    removed = len(result.removed)
    changed = len(result.changed)
    unchanged = len(result.unchanged)
    total = added + removed + changed + unchanged
    return DiffSummary(
        added=added,
        removed=removed,
        changed=changed,
        unchanged=unchanged,
        total=total,
    )


def format_summary(summary: DiffSummary) -> str:
    """Return a multi-line human-readable summary string."""
    lines = [
        summary.headline,
        f"  Added   : {summary.added}",
        f"  Removed : {summary.removed}",
        f"  Changed : {summary.changed}",
        f"  Same    : {summary.unchanged}",
        f"  Total   : {summary.total}",
    ]
    return "\n".join(lines)
