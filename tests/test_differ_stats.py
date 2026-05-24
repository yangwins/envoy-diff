"""Tests for envoy_diff.differ_stats."""

from __future__ import annotations

import pytest

from envoy_diff.differ import DiffResult
from envoy_diff.differ_stats import DiffStats, compute_stats, format_stats


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
# compute_stats
# ---------------------------------------------------------------------------

def test_compute_stats_empty_result():
    result = _make_result()
    stats = compute_stats(result)
    assert stats.total_keys == 0
    assert stats.change_rate == 0.0


def test_compute_stats_counts_added():
    result = _make_result(added={"A": "1", "B": "2"})
    stats = compute_stats(result)
    assert stats.added == 2
    assert stats.total_keys == 2


def test_compute_stats_counts_removed():
    result = _make_result(removed={"X": "old"})
    stats = compute_stats(result)
    assert stats.removed == 1


def test_compute_stats_counts_changed():
    result = _make_result(changed={"K": ("old", "new")})
    stats = compute_stats(result)
    assert stats.changed == 1


def test_compute_stats_counts_unchanged():
    result = _make_result(unchanged={"U": "same"})
    stats = compute_stats(result)
    assert stats.unchanged == 1


def test_compute_stats_change_rate_all_changed():
    result = _make_result(added={"A": "1"}, removed={"B": "2"}, changed={"C": ("x", "y")})
    stats = compute_stats(result)
    assert stats.change_rate == pytest.approx(1.0)


def test_compute_stats_change_rate_half():
    result = _make_result(changed={"A": ("x", "y")}, unchanged={"B": "z"})
    stats = compute_stats(result)
    assert stats.change_rate == pytest.approx(0.5)


def test_compute_stats_top_changed_keys_default_limit():
    added = {f"KEY_{i}": str(i) for i in range(10)}
    result = _make_result(added=added)
    stats = compute_stats(result)
    assert len(stats.top_changed_keys) == 5


def test_compute_stats_top_changed_keys_custom_limit():
    added = {f"KEY_{i}": str(i) for i in range(10)}
    result = _make_result(added=added)
    stats = compute_stats(result, top_n=3)
    assert len(stats.top_changed_keys) == 3


def test_compute_stats_top_changed_keys_are_sorted():
    result = _make_result(added={"ZEBRA": "1", "ALPHA": "2", "MANGO": "3"})
    stats = compute_stats(result, top_n=10)
    assert stats.top_changed_keys == sorted(stats.top_changed_keys)


def test_compute_stats_top_changed_keys_fewer_than_top_n():
    result = _make_result(added={"ONLY": "1"})
    stats = compute_stats(result, top_n=5)
    assert stats.top_changed_keys == ["ONLY"]


# ---------------------------------------------------------------------------
# as_dict
# ---------------------------------------------------------------------------

def test_as_dict_contains_all_keys():
    result = _make_result(added={"A": "1"}, unchanged={"B": "2"})
    d = compute_stats(result).as_dict()
    expected_keys = {"total_keys", "added", "removed", "changed", "unchanged", "change_rate", "top_changed_keys"}
    assert expected_keys == set(d.keys())


def test_as_dict_change_rate_rounded():
    result = _make_result(changed={"A": ("x", "y")}, unchanged={"B": "z"})
    d = compute_stats(result).as_dict()
    assert d["change_rate"] == 0.5


# ---------------------------------------------------------------------------
# format_stats
# ---------------------------------------------------------------------------

def test_format_stats_returns_string():
    result = _make_result(added={"A": "1"})
    output = format_stats(compute_stats(result))
    assert isinstance(output, str)


def test_format_stats_contains_total_keys():
    result = _make_result(added={"A": "1"}, unchanged={"B": "2"})
    output = format_stats(compute_stats(result))
    assert "2" in output


def test_format_stats_contains_top_keys_line():
    result = _make_result(added={"MY_KEY": "v"})
    output = format_stats(compute_stats(result))
    assert "MY_KEY" in output


def test_format_stats_no_top_keys_line_when_empty():
    result = _make_result(unchanged={"A": "1"})
    output = format_stats(compute_stats(result))
    assert "Top keys" not in output
