"""Integration tests: planner works with differ, masker, and filter."""
from __future__ import annotations

from envoy_diff.differ import diff_envs
from envoy_diff.filter import filter_env
from envoy_diff.masker import mask_env
from envoy_diff.planner import format_plan, plan_rollout


def test_plan_from_real_diff_has_correct_counts():
    base = {"A": "1", "B": "2", "C": "3"}
    head = {"B": "changed", "C": "3", "D": "4"}
    result = diff_envs(base, head)
    plan = plan_rollout(result)
    removals = next(p for p in plan.phases if p.name == "removals")
    changes = next(p for p in plan.phases if p.name == "changes")
    additions = next(p for p in plan.phases if p.name == "additions")
    assert "A" in removals.keys
    assert "B" in changes.keys
    assert "D" in additions.keys
    assert plan.total_steps() == 3


def test_plan_after_filter_only_includes_filtered_keys():
    base = {"APP_HOST": "old", "DB_URL": "db"}
    head = {"APP_HOST": "new", "DB_URL": "db"}
    filtered_base = filter_env(base, prefix="APP_")
    filtered_head = filter_env(head, prefix="APP_")
    result = diff_envs(filtered_base, filtered_head)
    plan = plan_rollout(result)
    all_keys = [k for p in plan.phases for k in p.keys]
    assert "APP_HOST" in all_keys
    assert "DB_URL" not in all_keys


def test_plan_masked_env_does_not_affect_phase_keys():
    base = {"SECRET_KEY": "abc", "PLAIN": "x"}
    head = {"SECRET_KEY": "xyz", "PLAIN": "x"}
    masked_base = mask_env(base)
    masked_head = mask_env(head)
    result = diff_envs(masked_base, masked_head)
    plan = plan_rollout(result)
    changes = next(p for p in plan.phases if p.name == "changes")
    # key name is still present even though value was masked
    assert "SECRET_KEY" in changes.keys


def test_plan_identical_envs_produces_empty_plan():
    env = {"X": "1", "Y": "2"}
    result = diff_envs(env, env.copy())
    plan = plan_rollout(result)
    assert plan.is_empty() is True
    assert plan.total_steps() == 0


def test_format_plan_full_workflow_output_is_string():
    base = {"OLD": "v"}
    head = {"NEW": "v"}
    result = diff_envs(base, head)
    output = format_plan(plan_rollout(result))
    assert isinstance(output, str)
    assert len(output) > 0
