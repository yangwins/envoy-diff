"""Tests for envoy_diff.filter module."""

import re
import pytest

from envoy_diff.filter import filter_env, filter_keys_by_regex


SAMPLE = {
    "APP_HOST": "localhost",
    "APP_PORT": "8080",
    "DB_HOST": "db.internal",
    "DB_PASSWORD": "secret",
    "LOG_LEVEL": "INFO",
    "AWS_ACCESS_KEY": "AKIA123",
}


def test_filter_env_no_filters_returns_all():
    result = filter_env(SAMPLE)
    assert result == SAMPLE


def test_filter_env_does_not_mutate_original():
    original = dict(SAMPLE)
    filter_env(original, exclude=["DB_*"])
    assert original == SAMPLE


def test_filter_env_prefix():
    result = filter_env(SAMPLE, prefix="APP_")
    assert set(result.keys()) == {"APP_HOST", "APP_PORT"}


def test_filter_env_include_glob():
    result = filter_env(SAMPLE, include=["DB_*"])
    assert set(result.keys()) == {"DB_HOST", "DB_PASSWORD"}


def test_filter_env_include_multiple_patterns():
    result = filter_env(SAMPLE, include=["APP_*", "LOG_*"])
    assert set(result.keys()) == {"APP_HOST", "APP_PORT", "LOG_LEVEL"}


def test_filter_env_exclude_glob():
    result = filter_env(SAMPLE, exclude=["DB_*"])
    assert "DB_HOST" not in result
    assert "DB_PASSWORD" not in result
    assert "APP_HOST" in result


def test_filter_env_exclude_multiple_patterns():
    result = filter_env(SAMPLE, exclude=["APP_*", "AWS_*"])
    assert set(result.keys()) == {"DB_HOST", "DB_PASSWORD", "LOG_LEVEL"}


def test_filter_env_include_and_exclude_combined():
    # include DB_* then exclude DB_PASSWORD
    result = filter_env(SAMPLE, include=["DB_*"], exclude=["*PASSWORD*"])
    assert set(result.keys()) == {"DB_HOST"}


def test_filter_env_prefix_and_exclude_combined():
    result = filter_env(SAMPLE, prefix="APP_", exclude=["*PORT*"])
    assert set(result.keys()) == {"APP_HOST"}


def test_filter_env_empty_env():
    result = filter_env({}, include=["APP_*"], prefix="APP_")
    assert result == {}


def test_filter_keys_by_regex_basic():
    result = filter_keys_by_regex(SAMPLE, r"^APP_")
    assert set(result.keys()) == {"APP_HOST", "APP_PORT"}


def test_filter_keys_by_regex_case_sensitive():
    result = filter_keys_by_regex(SAMPLE, r"app_")
    assert result == {}


def test_filter_keys_by_regex_partial_match():
    result = filter_keys_by_regex(SAMPLE, r"HOST")
    assert set(result.keys()) == {"APP_HOST", "DB_HOST"}


def test_filter_keys_by_regex_invalid_pattern_raises():
    with pytest.raises(re.error):
        filter_keys_by_regex(SAMPLE, r"[invalid")


def test_filter_keys_by_regex_no_match_returns_empty():
    result = filter_keys_by_regex(SAMPLE, r"^NONEXISTENT")
    assert result == {}
