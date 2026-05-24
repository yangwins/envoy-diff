"""planner.py — Generate a rollout plan from a DiffResult.

A rollout plan groups diff entries into ordered phases:
  1. removals  (lowest risk — stop using old keys first)
  2. changes   (medium risk — update existing keys)
  3. additions (deploy new keys last)

Each phase lists the affected keys so operators can apply
changes incrementally and verify between steps.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envoy_diff.differ import DiffResult


@dataclass
class RolloutPhase:
    name: str
    keys: List[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {"phase": self.name, "keys": sorted(self.keys)}


@dataclass
class RolloutPlan:
    phases: List[RolloutPhase] = field(default_factory=list)

    # ------------------------------------------------------------------
    def is_empty(self) -> bool:
        return all(len(p.keys) == 0 for p in self.phases)

    def total_steps(self) -> int:
        return sum(len(p.keys) for p in self.phases)

    def as_dict(self) -> dict:
        return {
            "total_steps": self.total_steps(),
            "phases": [p.as_dict() for p in self.phases],
        }


def plan_rollout(result: DiffResult) -> RolloutPlan:
    """Build a three-phase rollout plan from *result*."""
    removals = RolloutPhase(name="removals", keys=list(result.removed.keys()))
    changes = RolloutPhase(name="changes", keys=list(result.changed.keys()))
    additions = RolloutPhase(name="additions", keys=list(result.added.keys()))
    return RolloutPlan(phases=[removals, changes, additions])


def format_plan(plan: RolloutPlan) -> str:
    """Return a human-readable multi-line string for *plan*."""
    if plan.is_empty():
        return "No rollout steps required.\n"

    lines: List[str] = []
    for idx, phase in enumerate(plan.phases, start=1):
        if not phase.keys:
            continue
        lines.append(f"Phase {idx} — {phase.name} ({len(phase.keys)} key(s)):")
        for key in sorted(phase.keys):
            lines.append(f"  - {key}")
    lines.append("")
    return "\n".join(lines)
