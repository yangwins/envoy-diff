"""Tests for envoy_diff.redactor."""

import pytest

from envoy_diff.redactor import (
    DEFAULT_PLACEHOLDER,
    is_redacted,
    redact_all,
    redact_env,
    redact_keys,
)


# ---------------------------------------------------------------------------
# redact_keys
# ---------------------------------------------------------------------------

def test_redact_keys_replaces_specified_keys():
    env = {"A": "alpha", "B": "beta", "C": "gamma"}
    result = redact_keys(env, ["A", "C"])
    assert result["A"] == DEFAULT_PLACEHOLDER
    assert result["C"] == DEFAULT_PLACEHOLDER


def test_redact_keys_leaves_other_keys_unchanged():
    env = {"A": "alpha", "B": "beta"}
    result = redact_keys(env, ["A"])
    assert result["B"] == "beta"


def test_redact_keys_does_not_mutate_original():
    env = {"SECRET": "s3cr3t"}
    redact_keys(env, ["SECRET"])
    assert env["SECRET"] == "s3cr3t"


def test_redact_keys_unknown_key_is_ignored():
    env = {"A": "alpha"}
    result = redact_keys(env, ["MISSING"])
    assert result == {"A": "alpha"}


def test_redact_keys_custom_placeholder():
    env = {"TOKEN": "abc123"}
    result = redact_keys(env, ["TOKEN"], placeholder="***")
    assert result["TOKEN"] == "***"


def test_redact_keys_raises_on_non_dict():
    with pytest.raises(TypeError):
        redact_keys(["not", "a", "dict"], [])  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# redact_all
# ---------------------------------------------------------------------------

def test_redact_all_replaces_every_value():
    env = {"A": "1", "B": "2", "C": "3"}
    result = redact_all(env)
    assert all(v == DEFAULT_PLACEHOLDER for v in result.values())


def test_redact_all_preserves_keys():
    env = {"X": "x", "Y": "y"}
    result = redact_all(env)
    assert set(result.keys()) == {"X", "Y"}


def test_redact_all_empty_env_returns_empty():
    assert redact_all({}) == {}


def test_redact_all_raises_on_non_dict():
    with pytest.raises(TypeError):
        redact_all("not a dict")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# is_redacted
# ---------------------------------------------------------------------------

def test_is_redacted_true_for_default_placeholder():
    assert is_redacted(DEFAULT_PLACEHOLDER) is True


def test_is_redacted_false_for_real_value():
    assert is_redacted("real_value") is False


def test_is_redacted_custom_placeholder():
    assert is_redacted("***", placeholder="***") is True


# ---------------------------------------------------------------------------
# redact_env (high-level helper)
# ---------------------------------------------------------------------------

def test_redact_env_with_keys_redacts_only_those_keys():
    env = {"A": "alpha", "B": "beta"}
    result = redact_env(env, keys=["A"])
    assert result["A"] == DEFAULT_PLACEHOLDER
    assert result["B"] == "beta"


def test_redact_env_without_keys_redacts_all():
    env = {"A": "alpha", "B": "beta"}
    result = redact_env(env)
    assert all(v == DEFAULT_PLACEHOLDER for v in result.values())


def test_redact_env_empty_keys_list_redacts_nothing():
    env = {"A": "alpha"}
    result = redact_env(env, keys=[])
    assert result == {"A": "alpha"}
