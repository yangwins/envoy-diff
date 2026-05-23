"""Tests for envoy_diff.comparator."""
from __future__ import annotations

import pytest

from envoy_diff.comparator import (
    ComparisonContext,
    ComparisonResult,
    compare,
)


# ---------------------------------------------------------------------------
# ComparisonContext
# ---------------------------------------------------------------------------

def test_context_default_labels():
    ctx = ComparisonContext()
    assert ctx.left_label == "left"
    assert ctx.right_label == "right"


def test_context_custom_labels():
    ctx = ComparisonContext(left_label="staging", right_label="production")
    assert ctx.left_label == "staging"
    assert ctx.right_label == "production"


def test_context_as_dict_keys():
    ctx = ComparisonContext(left_label="a", right_label="b", description="test run")
    d = ctx.as_dict()
    assert set(d.keys()) == {"left_label", "right_label", "timestamp", "description"}


def test_context_timestamp_is_float():
    ctx = ComparisonContext()
    assert isinstance(ctx.timestamp, float)
    assert ctx.timestamp > 0


# ---------------------------------------------------------------------------
# compare()
# ---------------------------------------------------------------------------

def test_compare_returns_comparison_result():
    result = compare({"A": "1"}, {"A": "1"})
    assert isinstance(result, ComparisonResult)


def test_compare_no_differences():
    result = compare({"A": "1", "B": "2"}, {"A": "1", "B": "2"})
    assert result.diff.added == {}
    assert result.diff.removed == {}
    assert result.diff.changed == {}


def test_compare_detects_added_key():
    result = compare({}, {"NEW": "val"})
    assert "NEW" in result.diff.added


def test_compare_detects_removed_key():
    result = compare({"OLD": "val"}, {})
    assert "OLD" in result.diff.removed


def test_compare_detects_changed_key():
    result = compare({"K": "old"}, {"K": "new"})
    assert "K" in result.diff.changed


def test_compare_attaches_labels():
    result = compare({}, {}, left_label="staging", right_label="prod")
    assert result.context.left_label == "staging"
    assert result.context.right_label == "prod"


def test_compare_attaches_description():
    result = compare({}, {}, description="nightly check")
    assert result.context.description == "nightly check"


def test_compare_summary_counts_added():
    result = compare({}, {"X": "1", "Y": "2"})
    assert result.summary.added == 2


def test_compare_score_is_score_result():
    from envoy_diff.scorer import ScoreResult
    result = compare({"A": "1"}, {"A": "2"})
    assert isinstance(result.score, ScoreResult)


def test_compare_as_dict_structure():
    result = compare({"A": "1"}, {"A": "2"}, left_label="l", right_label="r")
    d = result.as_dict()
    assert "context" in d
    assert "summary" in d
    assert "score" in d
    assert "diff" in d


def test_compare_as_dict_diff_keys():
    result = compare({}, {})
    diff_dict = result.as_dict()["diff"]
    assert set(diff_dict.keys()) == {"added", "removed", "changed", "unchanged"}
