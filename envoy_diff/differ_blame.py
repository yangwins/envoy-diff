"""Blame module: annotate diff keys with who last changed them."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from envoy_diff.differ import DiffResult


@dataclass
class BlameEntry:
    key: str
    author: str
    timestamp: Optional[float] = None
    note: Optional[str] = None

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "author": self.author,
            "timestamp": self.timestamp,
            "note": self.note,
        }


@dataclass
class BlameReport:
    changed: Dict[str, BlameEntry] = field(default_factory=dict)
    added: Dict[str, BlameEntry] = field(default_factory=dict)
    removed: Dict[str, BlameEntry] = field(default_factory=dict)
    untracked: list = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "changed": {k: v.as_dict() for k, v in self.changed.items()},
            "added": {k: v.as_dict() for k, v in self.added.items()},
            "removed": {k: v.as_dict() for k, v in self.removed.items()},
            "untracked": sorted(self.untracked),
        }

    @property
    def is_fully_attributed(self) -> bool:
        return len(self.untracked) == 0


BlameMap = Dict[str, BlameEntry]


def blame_diff(result: DiffResult, blame_map: BlameMap) -> BlameReport:
    """Cross-reference a DiffResult with a blame map.

    Keys present in the diff but absent from *blame_map* are collected
    in ``untracked``.
    """
    report = BlameReport()

    for key in result.changed:
        if key in blame_map:
            report.changed[key] = blame_map[key]
        else:
            report.untracked.append(key)

    for key in result.added:
        if key in blame_map:
            report.added[key] = blame_map[key]
        else:
            report.untracked.append(key)

    for key in result.removed:
        if key in blame_map:
            report.removed[key] = blame_map[key]
        else:
            report.untracked.append(key)

    return report


def format_blame(report: BlameReport) -> str:
    """Return a human-readable blame summary."""
    lines: list[str] = []
    sections = [
        ("changed", report.changed),
        ("added", report.added),
        ("removed", report.removed),
    ]
    for label, entries in sections:
        if entries:
            lines.append(f"[{label}]")
            for key, entry in sorted(entries.items()):
                ts = f" @ {entry.timestamp}" if entry.timestamp else ""
                note = f" ({entry.note})" if entry.note else ""
                lines.append(f"  {key}: {entry.author}{ts}{note}")
    if report.untracked:
        lines.append("[untracked]")
        for key in sorted(report.untracked):
            lines.append(f"  {key}")
    return "\n".join(lines)
