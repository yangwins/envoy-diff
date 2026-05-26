"""Tests for envoy_diff.differ_blame."""
import pytest

from envoy_diff.differ import DiffResult
from envoy_diff.differ_blame import (
    BlameEntry,
    BlameReport,
    blame_diff,
    format_blame,
)


def _make_result(
    changed=None, added=None, removed=None, unchanged=None
) -> DiffResult:
    return DiffResult(
        changed=changed or {},
        added=added or {},
        removed=removed or {},
        unchanged=unchanged or {},
    )


def _entry(author="alice", ts=None, note=None) -> BlameEntry:
    return BlameEntry(key="", author=author, timestamp=ts, note=note)


# --- BlameEntry ---

def test_blame_entry_as_dict_has_expected_keys():
    e = BlameEntry(key="FOO", author="bob", timestamp=1.0, note="deploy")
    d = e.as_dict()
    assert set(d.keys()) == {"key", "author", "timestamp", "note"}


def test_blame_entry_as_dict_values():
    e = BlameEntry(key="X", author="carol", timestamp=None, note=None)
    assert e.as_dict()["author"] == "carol"
    assert e.as_dict()["timestamp"] is None


# --- BlameReport ---

def test_blame_report_is_fully_attributed_when_no_untracked():
    r = BlameReport()
    assert r.is_fully_attributed is True


def test_blame_report_not_fully_attributed_with_untracked():
    r = BlameReport(untracked=["MISSING"])
    assert r.is_fully_attributed is False


def test_blame_report_as_dict_structure():
    r = BlameReport()
    d = r.as_dict()
    assert "changed" in d and "added" in d and "removed" in d and "untracked" in d


# --- blame_diff ---

def test_blame_diff_attributes_changed_key():
    result = _make_result(changed={"DB_URL": ("old", "new")})
    bmap = {"DB_URL": BlameEntry(key="DB_URL", author="alice")}
    report = blame_diff(result, bmap)
    assert "DB_URL" in report.changed
    assert report.changed["DB_URL"].author == "alice"


def test_blame_diff_attributes_added_key():
    result = _make_result(added={"NEW_KEY": "val"})
    bmap = {"NEW_KEY": BlameEntry(key="NEW_KEY", author="bob")}
    report = blame_diff(result, bmap)
    assert "NEW_KEY" in report.added


def test_blame_diff_attributes_removed_key():
    result = _make_result(removed={"OLD_KEY": "val"})
    bmap = {"OLD_KEY": BlameEntry(key="OLD_KEY", author="carol")}
    report = blame_diff(result, bmap)
    assert "OLD_KEY" in report.removed


def test_blame_diff_untracked_changed_key():
    result = _make_result(changed={"UNKNOWN": ("a", "b")})
    report = blame_diff(result, {})
    assert "UNKNOWN" in report.untracked
    assert report.is_fully_attributed is False


def test_blame_diff_untracked_added_key():
    result = _make_result(added={"GHOST": "v"})
    report = blame_diff(result, {})
    assert "GHOST" in report.untracked


def test_blame_diff_empty_diff_empty_report():
    result = _make_result()
    report = blame_diff(result, {})
    assert report.is_fully_attributed
    assert report.changed == {}
    assert report.added == {}
    assert report.removed == {}


def test_blame_diff_unchanged_keys_ignored():
    result = _make_result(unchanged={"STABLE": "v"})
    bmap = {"STABLE": BlameEntry(key="STABLE", author="dave")}
    report = blame_diff(result, bmap)
    assert "STABLE" not in report.changed
    assert "STABLE" not in report.added
    assert "STABLE" not in report.removed
    assert "STABLE" not in report.untracked


# --- format_blame ---

def test_format_blame_includes_author():
    result = _make_result(changed={"KEY": ("a", "b")})
    bmap = {"KEY": BlameEntry(key="KEY", author="eve")}
    report = blame_diff(result, bmap)
    output = format_blame(report)
    assert "eve" in output
    assert "KEY" in output


def test_format_blame_untracked_section():
    result = _make_result(added={"MYSTERY": "x"})
    report = blame_diff(result, {})
    output = format_blame(report)
    assert "untracked" in output
    assert "MYSTERY" in output


def test_format_blame_empty_report_is_empty_string():
    report = BlameReport()
    assert format_blame(report) == ""


def test_format_blame_includes_timestamp():
    result = _make_result(removed={"OLD": "v"})
    bmap = {"OLD": BlameEntry(key="OLD", author="frank", timestamp=1700000000.0)}
    report = blame_diff(result, bmap)
    output = format_blame(report)
    assert "1700000000.0" in output
