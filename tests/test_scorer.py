"""Tests for envoy_diff.scorer."""

import pytest

from envoy_diff.differ import DiffResult
from envoy_diff.scorer import (
    ADD_WEIGHT,
    CHANGE_WEIGHT,
    REMOVE_WEIGHT,
    SENSITIVE_MULTIPLIER,
    ScoreResult,
    score_diff,
)


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


def test_score_empty_diff_is_zero():
    result = _make_result()
    sr = score_diff(result)
    assert sr.score == 0.0


def test_score_empty_diff_risk_label_is_none():
    result = _make_result()
    sr = score_diff(result)
    assert sr.risk_label == "none"


def test_score_single_added_key():
    result = _make_result(added={"FOO": "bar"})
    sr = score_diff(result)
    assert sr.added_score == ADD_WEIGHT
    assert sr.score == ADD_WEIGHT


def test_score_single_removed_key():
    result = _make_result(removed={"FOO": "bar"})
    sr = score_diff(result)
    assert sr.removed_score == REMOVE_WEIGHT
    assert sr.score == REMOVE_WEIGHT


def test_score_single_changed_key():
    result = _make_result(changed={"FOO": ("old", "new")})
    sr = score_diff(result)
    assert sr.changed_score == CHANGE_WEIGHT
    assert sr.score == CHANGE_WEIGHT


def test_score_sensitive_added_key_multiplied():
    result = _make_result(added={"API_SECRET": "x"})
    sr = score_diff(result)
    assert sr.added_score == ADD_WEIGHT * SENSITIVE_MULTIPLIER


def test_score_sensitive_removed_key_multiplied():
    result = _make_result(removed={"DB_PASSWORD": "x"})
    sr = score_diff(result)
    assert sr.removed_score == REMOVE_WEIGHT * SENSITIVE_MULTIPLIER


def test_score_sensitive_changed_key_multiplied():
    result = _make_result(changed={"AUTH_TOKEN": ("a", "b")})
    sr = score_diff(result)
    assert sr.changed_score == CHANGE_WEIGHT * SENSITIVE_MULTIPLIER


def test_score_mixed_keys_sums_correctly():
    result = _make_result(
        added={"FOO": "1"},
        removed={"BAR": "2"},
        changed={"BAZ": ("old", "new")},
    )
    sr = score_diff(result)
    expected = ADD_WEIGHT + REMOVE_WEIGHT + CHANGE_WEIGHT
    assert sr.score == round(expected, 4)


def test_risk_label_low():
    result = _make_result(added={"X": "1"})
    sr = score_diff(result)
    assert sr.risk_label == "low"


def test_risk_label_medium():
    # 6 added non-sensitive keys => 6.0
    result = _make_result(added={f"K{i}": str(i) for i in range(6)})
    sr = score_diff(result)
    assert sr.risk_label == "medium"


def test_risk_label_high():
    # 10 removed non-sensitive keys => 20.0
    result = _make_result(removed={f"K{i}": str(i) for i in range(10)})
    sr = score_diff(result)
    assert sr.risk_label == "high"


def test_as_dict_contains_expected_keys():
    result = _make_result(added={"FOO": "1"})
    d = score_diff(result).as_dict()
    assert set(d.keys()) == {"score", "added_score", "removed_score", "changed_score", "risk_label"}


def test_score_result_is_frozen():
    result = _make_result()
    sr = score_diff(result)
    with pytest.raises(Exception):
        sr.score = 99  # type: ignore[misc]
