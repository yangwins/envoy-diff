"""comparator.py – named environment comparison with metadata.

Allows comparing two named environments (e.g. 'staging' vs 'production')
and attaching context such as labels, timestamps, and diff scores.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional

from envoy_diff.differ import DiffResult, diff_envs
from envoy_diff.scorer import ScoreResult, score_diff
from envoy_diff.summarizer import DiffSummary, summarize


@dataclass
class ComparisonContext:
    """Metadata attached to a comparison run."""

    left_label: str = "left"
    right_label: str = "right"
    timestamp: float = field(default_factory=time.time)
    description: str = ""

    def as_dict(self) -> dict:
        return {
            "left_label": self.left_label,
            "right_label": self.right_label,
            "timestamp": self.timestamp,
            "description": self.description,
        }


@dataclass
class ComparisonResult:
    """Full result of a named environment comparison."""

    context: ComparisonContext
    diff: DiffResult
    summary: DiffSummary
    score: ScoreResult

    def as_dict(self) -> dict:
        return {
            "context": self.context.as_dict(),
            "summary": self.summary.as_dict(),
            "score": self.score.as_dict(),
            "diff": {
                "added": self.diff.added,
                "removed": self.diff.removed,
                "changed": self.diff.changed,
                "unchanged": self.diff.unchanged,
            },
        }


def compare(
    left: dict[str, str],
    right: dict[str, str],
    left_label: str = "left",
    right_label: str = "right",
    description: str = "",
) -> ComparisonResult:
    """Compare two environments and return a rich ComparisonResult."""
    context = ComparisonContext(
        left_label=left_label,
        right_label=right_label,
        description=description,
    )
    diff = diff_envs(left, right)
    summary = summarize(diff)
    score = score_diff(diff)
    return ComparisonResult(context=context, diff=diff, summary=summary, score=score)
