"""Unit tests for envoy_diff.planner."""
from __future__ import annotations

import pytest

from envoy_diff.differ import DiffResult
from envoy_diff.planner import (
    RolloutPhase,
    RolloutPlan,
    format_plan,
    plan_rollout,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _make_result(
    added=None,
    removed=None,
    changed=None,
    unchanged=None,
) -> DiffResult:
    return DiffResult(
        added=added or {},
        removed=removed or {},
        changed=changed or {},
        unchanged=unchanged or {},
    )


# ---------------------------------------------------------------------------
# RolloutPhase
# ---------------------------------------------------------------------------

def test_rollout_phase_as_dict_contains_name():
    phase = RolloutPhase(name="additions", keys=["B", "A"])
    d = phase.as_dict()
    assert d["phase"] == "additions"


def test_rollout_phase_as_dict_keys_are_sorted():
    phase = RolloutPhase(name="changes", keys=["Z", "A", "M"])
    assert phase.as_dict()["keys"] == ["A", "M", "Z"]


# ---------------------------------------------------------------------------
# RolloutPlan
# ---------------------------------------------------------------------------

def test_rollout_plan_is_empty_when_all_phases_empty():
    plan = RolloutPlan(phases=[RolloutPhase("removals"), RolloutPhase("additions")])
    assert plan.is_empty() is True


def test_rollout_plan_not_empty_when_phase_has_keys():
    plan = RolloutPlan(phases=[RolloutPhase("additions", keys=["FOO"])])
    assert plan.is_empty() is False


def test_rollout_plan_total_steps_sums_all_phases():
    plan = RolloutPlan(
        phases=[
            RolloutPhase("removals", keys=["A"]),
            RolloutPhase("changes", keys=["B", "C"]),
            RolloutPhase("additions", keys=["D"]),
        ]
    )
    assert plan.total_steps() == 4


def test_rollout_plan_as_dict_structure():
    plan = RolloutPlan(phases=[RolloutPhase("removals", keys=["X"])])
    d = plan.as_dict()
    assert "total_steps" in d
    assert "phases" in d
    assert d["total_steps"] == 1


# ---------------------------------------------------------------------------
# plan_rollout
# ---------------------------------------------------------------------------

def test_plan_rollout_returns_rollout_plan():
    result = _make_result()
    plan = plan_rollout(result)
    assert isinstance(plan, RolloutPlan)


def test_plan_rollout_three_phases():
    plan = plan_rollout(_make_result())
    assert len(plan.phases) == 3


def test_plan_rollout_phase_names():
    plan = plan_rollout(_make_result())
    names = [p.name for p in plan.phases]
    assert names == ["removals", "changes", "additions"]


def test_plan_rollout_added_keys_in_additions_phase():
    result = _make_result(added={"NEW_KEY": "val"})
    plan = plan_rollout(result)
    additions = next(p for p in plan.phases if p.name == "additions")
    assert "NEW_KEY" in additions.keys


def test_plan_rollout_removed_keys_in_removals_phase():
    result = _make_result(removed={"OLD_KEY": "val"})
    plan = plan_rollout(result)
    removals = next(p for p in plan.phases if p.name == "removals")
    assert "OLD_KEY" in removals.keys


def test_plan_rollout_changed_keys_in_changes_phase():
    result = _make_result(changed={"EXISTING": ("old", "new")})
    plan = plan_rollout(result)
    changes = next(p for p in plan.phases if p.name == "changes")
    assert "EXISTING" in changes.keys


def test_plan_rollout_unchanged_keys_not_in_any_phase():
    result = _make_result(unchanged={"STABLE": "value"})
    plan = plan_rollout(result)
    all_keys = [k for p in plan.phases for k in p.keys]
    assert "STABLE" not in all_keys


def test_plan_rollout_empty_diff_is_empty():
    plan = plan_rollout(_make_result())
    assert plan.is_empty() is True


# ---------------------------------------------------------------------------
# format_plan
# ---------------------------------------------------------------------------

def test_format_plan_empty_returns_no_steps_message():
    plan = plan_rollout(_make_result())
    output = format_plan(plan)
    assert "No rollout steps required" in output


def test_format_plan_lists_phase_header():
    result = _make_result(added={"FOO": "bar"})
    output = format_plan(plan_rollout(result))
    assert "additions" in output


def test_format_plan_lists_key_under_phase():
    result = _make_result(removed={"GONE": "x"})
    output = format_plan(plan_rollout(result))
    assert "GONE" in output


def test_format_plan_ends_with_newline():
    result = _make_result(changed={"K": ("a", "b")})
    output = format_plan(plan_rollout(result))
    assert output.endswith("\n")


def test_format_plan_skips_empty_phases():
    result = _make_result(added={"ONLY": "1"})
    output = format_plan(plan_rollout(result))
    assert "removals" not in output
    assert "changes" not in output
