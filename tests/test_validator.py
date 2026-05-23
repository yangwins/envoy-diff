"""Tests for envoy_diff.validator."""

import pytest

from envoy_diff.validator import ValidationResult, assert_valid, validate_env


# ---------------------------------------------------------------------------
# ValidationResult
# ---------------------------------------------------------------------------

def test_validation_result_valid_is_truthy():
    assert ValidationResult(valid=True)


def test_validation_result_invalid_is_falsy():
    assert not ValidationResult(valid=False, errors=["oops"])


# ---------------------------------------------------------------------------
# validate_env — happy paths
# ---------------------------------------------------------------------------

def test_validate_env_empty_dict_is_valid():
    result = validate_env({})
    assert result.valid
    assert result.errors == []


def test_validate_env_normal_dict_is_valid():
    result = validate_env({"HOST": "localhost", "PORT": "8080"})
    assert result.valid


def test_validate_env_allows_empty_values_by_default():
    result = validate_env({"OPTIONAL": ""})
    assert result.valid


def test_validate_env_required_keys_present():
    result = validate_env(
        {"HOST": "localhost", "PORT": "8080"},
        required_keys=["HOST", "PORT"],
    )
    assert result.valid


# ---------------------------------------------------------------------------
# validate_env — error paths
# ---------------------------------------------------------------------------

def test_validate_env_non_string_value_is_invalid():
    result = validate_env({"PORT": 8080})  # type: ignore[dict-item]
    assert not result.valid
    assert any("PORT" in e for e in result.errors)


def test_validate_env_empty_value_when_disallowed():
    result = validate_env({"KEY": ""}, allow_empty_values=False)
    assert not result.valid
    assert any("KEY" in e for e in result.errors)


def test_validate_env_missing_required_key():
    result = validate_env({"HOST": "localhost"}, required_keys=["HOST", "PORT"])
    assert not result.valid
    assert any("PORT" in e for e in result.errors)


def test_validate_env_multiple_errors_all_reported():
    result = validate_env(
        {"A": "", "B": ""},
        allow_empty_values=False,
        required_keys=["C"],
    )
    assert not result.valid
    assert len(result.errors) == 3  # A empty, B empty, C missing


# ---------------------------------------------------------------------------
# assert_valid
# ---------------------------------------------------------------------------

def test_assert_valid_does_not_raise_for_valid_env():
    assert_valid({"HOST": "localhost"})  # should not raise


def test_assert_valid_raises_value_error_on_missing_required():
    with pytest.raises(ValueError, match="DATABASE_URL"):
        assert_valid({}, required_keys=["DATABASE_URL"])


def test_assert_valid_includes_label_in_message():
    with pytest.raises(ValueError, match="staging"):
        assert_valid({"X": ""}, allow_empty_values=False, label="staging")


def test_assert_valid_raises_on_non_string_value():
    with pytest.raises(ValueError):
        assert_valid({"NUM": 42})  # type: ignore[dict-item]
