"""DiffContext: attach metadata (labels, timestamp) to a diff operation."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from envoy_diff.differ import DiffResult, diff_envs


@dataclass
class DiffContext:
    """Wraps a DiffResult with contextual metadata."""

    result: DiffResult
    left_label: str = "left"
    right_label: str = "right"
    timestamp: float = field(default_factory=time.time)
    description: Optional[str] = None

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def has_differences(self) -> bool:
        """Return True when the wrapped diff contains any differences."""
        return self.result.has_differences()

    def as_dict(self) -> Dict[str, Any]:
        """Serialise the context and its diff to a plain dictionary."""
        return {
            "left_label": self.left_label,
            "right_label": self.right_label,
            "timestamp": self.timestamp,
            "description": self.description,
            "counts": self.result.counts(),
            "added": self.result.added,
            "removed": self.result.removed,
            "changed": {
                k: {"left": lv, "right": rv}
                for k, (lv, rv) in self.result.changed.items()
            },
            "unchanged": self.result.unchanged,
        }


def diff_with_context(
    left: Dict[str, str],
    right: Dict[str, str],
    *,
    left_label: str = "left",
    right_label: str = "right",
    description: Optional[str] = None,
) -> DiffContext:
    """Diff two environment dicts and wrap the result in a DiffContext.

    Parameters
    ----------
    left, right:
        Environment dictionaries to compare.
    left_label, right_label:
        Human-readable names for each side (e.g. ``"staging"``, ``"production"``).
    description:
        Optional free-text note stored alongside the diff.
    """
    result = diff_envs(left, right)
    return DiffContext(
        result=result,
        left_label=left_label,
        right_label=right_label,
        description=description,
    )
