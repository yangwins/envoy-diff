"""Integration tests for differ_blame with real differ output."""
from envoy_diff.differ import diff_envs
from envoy_diff.differ_blame import BlameEntry, blame_diff, format_blame


def _entry(author: str, ts: float = None) -> BlameEntry:
    return BlameEntry(key="", author=author, timestamp=ts)


def test_blame_after_real_diff_changed_key():
    staging = {"DB_HOST": "old-host"}
    production = {"DB_HOST": "new-host"}
    result = diff_envs(staging, production)
    bmap = {"DB_HOST": BlameEntry(key="DB_HOST", author="ops-team")}
    report = blame_diff(result, bmap)
    assert "DB_HOST" in report.changed
    assert report.changed["DB_HOST"].author == "ops-team"


def test_blame_after_real_diff_added_key():
    staging = {}
    production = {"FEATURE_FLAG": "true"}
    result = diff_envs(staging, production)
    bmap = {"FEATURE_FLAG": BlameEntry(key="FEATURE_FLAG", author="dev")}
    report = blame_diff(result, bmap)
    assert "FEATURE_FLAG" in report.added


def test_blame_after_real_diff_removed_key():
    staging = {"DEPRECATED": "1"}
    production = {}
    result = diff_envs(staging, production)
    bmap = {"DEPRECATED": BlameEntry(key="DEPRECATED", author="cleanup-bot")}
    report = blame_diff(result, bmap)
    assert "DEPRECATED" in report.removed


def test_blame_fully_attributed_when_all_keys_mapped():
    staging = {"A": "1", "B": "old"}
    production = {"B": "new", "C": "3"}
    result = diff_envs(staging, production)
    bmap = {
        "A": BlameEntry(key="A", author="alice"),
        "B": BlameEntry(key="B", author="bob"),
        "C": BlameEntry(key="C", author="carol"),
    }
    report = blame_diff(result, bmap)
    assert report.is_fully_attributed


def test_blame_untracked_when_keys_missing_from_map():
    staging = {"X": "v1"}
    production = {"X": "v2", "Y": "new"}
    result = diff_envs(staging, production)
    report = blame_diff(result, {})
    assert "X" in report.untracked
    assert "Y" in report.untracked


def test_format_blame_full_workflow_is_string():
    staging = {"HOST": "a", "OLD": "gone"}
    production = {"HOST": "b", "NEW": "here"}
    result = diff_envs(staging, production)
    bmap = {
        "HOST": BlameEntry(key="HOST", author="sre", timestamp=1700000000.0),
        "OLD": BlameEntry(key="OLD", author="ops"),
        "NEW": BlameEntry(key="NEW", author="dev", note="feature-x"),
    }
    report = blame_diff(result, bmap)
    output = format_blame(report)
    assert isinstance(output, str)
    assert "sre" in output
    assert "feature-x" in output
