"""Diff scorer — assigns a numeric risk score to a DiffResult.

Score is computed as a weighted sum:
  - each added key contributes ADD_WEIGHT points
  - each removed key contributes REMOVE_WEIGHT points
  - each changed key contributes CHANGE_WEIGHT points
  - sensitive keys (detected via masker.is_sensitive) multiply their
    contribution by SENSITIVE_MULTIPLIER
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from envoy_diff.differ import DiffResult
from envoy_diff.masker import is_sensitive

ADD_WEIGHT: float = 1.0
REMOVE_WEIGHT: float = 2.0
CHANGE_WEIGHT: float = 1.5
SENSITIVE_MULTIPLIER: float = 3.0


@dataclass(frozen=True)
class ScoreResult:
    score: float
    added_score: float
    removed_score: float
    changed_score: float

    @property
    def risk_label(self) -> str:
        """Return a human-readable risk label based on the total score."""
        if self.score == 0:
            return "none"
        if self.score < 5:
            return "low"
        if self.score < 15:
            return "medium"
        return "high"

    def as_dict(self) -> dict:
        return {
            "score": self.score,
            "added_score": self.added_score,
            "removed_score": self.removed_score,
            "changed_score": self.changed_score,
            "risk_label": self.risk_label,
        }


def _multiplier(key: str) -> float:
    return SENSITIVE_MULTIPLIER if is_sensitive(key) else 1.0


def score_diff(result: DiffResult) -> ScoreResult:
    """Compute a ScoreResult for the given DiffResult."""
    added_score = sum(
        ADD_WEIGHT * _multiplier(k) for k in result.added
    )
    removed_score = sum(
        REMOVE_WEIGHT * _multiplier(k) for k in result.removed
    )
    changed_score = sum(
        CHANGE_WEIGHT * _multiplier(k) for k in result.changed
    )
    total = round(added_score + removed_score + changed_score, 4)
    return ScoreResult(
        score=total,
        added_score=round(added_score, 4),
        removed_score=round(removed_score, 4),
        changed_score=round(changed_score, 4),
    )
