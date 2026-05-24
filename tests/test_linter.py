"""Tests for envoy_diff.linter."""
import pytest
from envoy_diff.linter import (
    LintViolation,
    LintResult,
    lint_env,
    lint_envs,
)


# ---------------------------------------------------------------------------
# LintViolation
# ---------------------------------------------------------------------------

def test_lint_violation_as_dict_has_key_and_reason():
    v = LintViolation(key="bad-key", reason="some reason")
    d = v.as_dict()
    assert d["key"] == "bad-key"
    assert d["reason"] == "some reason"


# ---------------------------------------------------------------------------
# LintResult
# ---------------------------------------------------------------------------

def test_lint_result_passed_when_no_violations():
    result = LintResult()
    assert result.passed is True


def test_lint_result_failed_when_violations():
    result = LintResult(violations=[LintViolation(key="x", reason="r")])
    assert result.passed is False


def test_lint_result_as_dict_structure():
    result = LintResult(violations=[LintViolation(key="x", reason="r")])
    d = result.as_dict()
    assert d["passed"] is False
    assert d["violation_count"] == 1
    assert isinstance(d["violations"], list)


# ---------------------------------------------------------------------------
# lint_env – valid keys
# ---------------------------------------------------------------------------

def test_lint_env_empty_dict_passes():
    assert lint_env({}).passed is True


def test_lint_env_valid_upper_snake_case_passes():
    assert lint_env({"APP_PORT": "8080", "DB_HOST": "localhost"}).passed is True


def test_lint_env_single_letter_key_passes():
    assert lint_env({"X": "1"}).passed is True


def test_lint_env_underscore_prefix_passes():
    assert lint_env({"_INTERNAL": "1"}).passed is True


# ---------------------------------------------------------------------------
# lint_env – invalid keys
# ---------------------------------------------------------------------------

def test_lint_env_lowercase_key_fails():
    result = lint_env({"app_port": "8080"})
    assert result.passed is False
    assert result.violations[0].key == "app_port"


def test_lint_env_mixed_case_key_fails():
    result = lint_env({"AppPort": "8080"})
    assert result.passed is False


def test_lint_env_key_starting_with_digit_fails():
    result = lint_env({"1_KEY": "v"})
    assert result.passed is False
    reasons = [v.reason for v in result.violations]
    assert any("digit" in r for r in reasons)


def test_lint_env_key_with_hyphen_fails():
    result = lint_env({"MY-KEY": "v"})
    assert result.passed is False
    reasons = [v.reason for v in result.violations]
    assert any("invalid characters" in r for r in reasons)


def test_lint_env_multiple_invalid_keys_all_reported():
    result = lint_env({"bad-key": "1", "another_bad": "2", "GOOD_KEY": "3"})
    bad_keys = {v.key for v in result.violations}
    assert "bad-key" in bad_keys
    assert "another_bad" in bad_keys
    assert "GOOD_KEY" not in bad_keys


def test_lint_env_raises_on_non_dict():
    with pytest.raises(TypeError):
        lint_env(["KEY=VALUE"])  # type: ignore


# ---------------------------------------------------------------------------
# lint_envs – multiple dicts
# ---------------------------------------------------------------------------

def test_lint_envs_aggregates_violations():
    result = lint_envs({"bad-a": "1"}, {"bad-b": "2"})
    keys = {v.key for v in result.violations}
    assert "bad-a" in keys
    assert "bad-b" in keys


def test_lint_envs_passes_when_all_valid():
    result = lint_envs({"APP_ENV": "prod"}, {"DB_PORT": "5432"})
    assert result.passed is True


def test_lint_envs_empty_call_passes():
    assert lint_envs().passed is True
