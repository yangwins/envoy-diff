"""Tests for envoy_diff.summarizer."""

import pytest

from envoy_diff.differ import DiffResult
from envoy_diff.summarizer import DiffSummary, format_summary, summarize


def _make_result(
    added=None, removed=None, changed=None, unchanged=None
) -> DiffResult:
    return DiffResult(
        added=added or {},
        removed=removed or {},
        changed=changed or {},
        unchanged=unchanged or {},
    )


# --- summarize() ---

def test_summarize_empty_result():
    result = _make_result()
    s = summarize(result)
    assert s.added == 0
    assert s.removed == 0
    assert s.changed == 0
    assert s.unchanged == 0
    assert s.total == 0


def test_summarize_counts_added():
    result = _make_result(added={"A": "1", "B": "2"})
    s = summarize(result)
    assert s.added == 2
    assert s.total == 2


def test_summarize_counts_removed():
    result = _make_result(removed={"X": "old"})
    s = summarize(result)
    assert s.removed == 1
    assert s.total == 1


def test_summarize_counts_changed():
    result = _make_result(changed={"K": ("old", "new")})
    s = summarize(result)
    assert s.changed == 1


def test_summarize_counts_unchanged():
    result = _make_result(unchanged={"SAME": "val"})
    s = summarize(result)
    assert s.unchanged == 1


def test_summarize_total_is_sum_of_all():
    result = _make_result(
        added={"A": "1"},
        removed={"B": "2"},
        changed={"C": ("x", "y")},
        unchanged={"D": "d"},
    )
    s = summarize(result)
    assert s.total == 4


# --- DiffSummary.headline ---

def test_headline_identical():
    s = DiffSummary(added=0, removed=0, changed=0, unchanged=5, total=5)
    assert s.headline == "Environments are identical"


def test_headline_with_changes():
    s = DiffSummary(added=2, removed=1, changed=3, unchanged=0, total=6)
    assert "2 added" in s.headline
    assert "1 removed" in s.headline
    assert "3 changed" in s.headline


def test_headline_only_added():
    s = DiffSummary(added=4, removed=0, changed=0, unchanged=0, total=4)
    assert s.headline == "4 added"


# --- DiffSummary.as_dict ---

def test_as_dict_keys():
    s = DiffSummary(added=1, removed=2, changed=3, unchanged=4, total=10)
    d = s.as_dict()
    assert set(d.keys()) == {"added", "removed", "changed", "unchanged", "total"}


def test_as_dict_values():
    s = DiffSummary(added=1, removed=2, changed=3, unchanged=4, total=10)
    assert s.as_dict()["total"] == 10


# --- format_summary() ---

def test_format_summary_contains_headline():
    result = _make_result(added={"K": "v"})
    s = summarize(result)
    text = format_summary(s)
    assert "1 added" in text


def test_format_summary_multiline():
    result = _make_result()
    text = format_summary(summarize(result))
    assert "\n" in text


def test_format_summary_shows_total():
    result = _make_result(unchanged={"A": "1", "B": "2"})
    text = format_summary(summarize(result))
    assert "2" in text
