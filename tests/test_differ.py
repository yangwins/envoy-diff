"""Tests for the envoy_diff.differ module."""

import pytest
from envoy_diff.differ import DiffResult, diff_envs


SOURCE = {
    "APP_ENV": "production",
    "DB_HOST": "prod-db.internal",
    "LOG_LEVEL": "WARNING",
    "SECRET_KEY": "abc123",
}

TARGET = {
    "APP_ENV": "staging",
    "DB_HOST": "prod-db.internal",
    "LOG_LEVEL": "DEBUG",
    "NEW_FEATURE_FLAG": "true",
}


def test_diff_envs_detects_added_keys():
    result = diff_envs(SOURCE, TARGET)
    assert "NEW_FEATURE_FLAG" in result.added
    assert result.added["NEW_FEATURE_FLAG"] == "true"


def test_diff_envs_detects_removed_keys():
    result = diff_envs(SOURCE, TARGET)
    assert "SECRET_KEY" in result.removed
    assert result.removed["SECRET_KEY"] == "abc123"


def test_diff_envs_detects_changed_keys():
    result = diff_envs(SOURCE, TARGET)
    assert "APP_ENV" in result.changed
    assert result.changed["APP_ENV"] == ("production", "staging")
    assert "LOG_LEVEL" in result.changed
    assert result.changed["LOG_LEVEL"] == ("WARNING", "DEBUG")


def test_diff_envs_detects_unchanged_keys():
    result = diff_envs(SOURCE, TARGET)
    assert "DB_HOST" in result.unchanged


def test_diff_envs_no_differences():
    result = diff_envs(SOURCE, SOURCE)
    assert not result.has_differences
    assert result.summary == "No differences found."


def test_diff_envs_has_differences():
    result = diff_envs(SOURCE, TARGET)
    assert result.has_differences


def test_diff_envs_summary_contains_counts():
    result = diff_envs(SOURCE, TARGET)
    assert "added" in result.summary
    assert "removed" in result.summary
    assert "changed" in result.summary


def test_diff_envs_ignore_keys():
    result = diff_envs(SOURCE, TARGET, ignore_keys={"APP_ENV", "NEW_FEATURE_FLAG", "SECRET_KEY"})
    assert "APP_ENV" not in result.changed
    assert "NEW_FEATURE_FLAG" not in result.added
    assert "SECRET_KEY" not in result.removed


def test_diff_envs_empty_source():
    result = diff_envs({}, TARGET)
    assert set(result.added.keys()) == set(TARGET.keys())
    assert not result.removed
    assert not result.changed


def test_diff_envs_empty_target():
    result = diff_envs(SOURCE, {})
    assert set(result.removed.keys()) == set(SOURCE.keys())
    assert not result.added
    assert not result.changed


def test_diff_envs_raises_on_invalid_source():
    with pytest.raises(TypeError, match="source must be a dict"):
        diff_envs("not-a-dict", TARGET)


def test_diff_envs_raises_on_invalid_target():
    with pytest.raises(TypeError, match="target must be a dict"):
        diff_envs(SOURCE, ["not", "a", "dict"])


def test_diff_result_defaults_are_empty():
    result = DiffResult()
    assert result.added == {}
    assert result.removed == {}
    assert result.changed == {}
    assert result.unchanged == {}
    assert not result.has_differences
