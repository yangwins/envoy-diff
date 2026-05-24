"""Tests for envoy_diff.differ_context."""
from __future__ import annotations

import time

import pytest

from envoy_diff.differ_context import DiffContext, diff_with_context
from envoy_diff.differ import diff_envs


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_LEFT = {"A": "1", "B": "2", "C": "3"}
_RIGHT = {"A": "1", "B": "99", "D": "4"}


def _ctx(**kwargs) -> DiffContext:
    return diff_with_context(_LEFT, _RIGHT, **kwargs)


# ---------------------------------------------------------------------------
# diff_with_context factory
# ---------------------------------------------------------------------------


def test_diff_with_context_returns_diff_context():
    ctx = _ctx()
    assert isinstance(ctx, DiffContext)


def test_diff_with_context_default_labels():
    ctx = _ctx()
    assert ctx.left_label == "left"
    assert ctx.right_label == "right"


def test_diff_with_context_custom_labels():
    ctx = _ctx(left_label="staging", right_label="production")
    assert ctx.left_label == "staging"
    assert ctx.right_label == "production"


def test_diff_with_context_description_default_is_none():
    ctx = _ctx()
    assert ctx.description is None


def test_diff_with_context_custom_description():
    ctx = _ctx(description="nightly comparison")
    assert ctx.description == "nightly comparison"


def test_diff_with_context_timestamp_is_recent():
    before = time.time()
    ctx = _ctx()
    after = time.time()
    assert before <= ctx.timestamp <= after


# ---------------------------------------------------------------------------
# has_differences
# ---------------------------------------------------------------------------


def test_has_differences_true_when_diff():
    ctx = _ctx()
    assert ctx.has_differences() is True


def test_has_differences_false_when_identical():
    ctx = diff_with_context({"X": "1"}, {"X": "1"})
    assert ctx.has_differences() is False


# ---------------------------------------------------------------------------
# as_dict
# ---------------------------------------------------------------------------


def test_as_dict_contains_labels():
    ctx = _ctx(left_label="a", right_label="b")
    d = ctx.as_dict()
    assert d["left_label"] == "a"
    assert d["right_label"] == "b"


def test_as_dict_contains_counts():
    ctx = _ctx()
    d = ctx.as_dict()
    counts = d["counts"]
    assert counts["added"] == 1   # D added
    assert counts["removed"] == 1  # C removed
    assert counts["changed"] == 1  # B changed


def test_as_dict_changed_has_left_right_structure():
    ctx = _ctx()
    d = ctx.as_dict()
    assert d["changed"]["B"] == {"left": "2", "right": "99"}


def test_as_dict_added_key_present():
    ctx = _ctx()
    assert "D" in ctx.as_dict()["added"]


def test_as_dict_removed_key_present():
    ctx = _ctx()
    assert "C" in ctx.as_dict()["removed"]


def test_as_dict_timestamp_matches_context():
    ctx = _ctx()
    assert ctx.as_dict()["timestamp"] == ctx.timestamp


def test_as_dict_description_included():
    ctx = _ctx(description="test run")
    assert ctx.as_dict()["description"] == "test run"
