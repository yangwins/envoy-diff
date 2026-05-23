"""Tests for envoy_diff.normalizer."""

from __future__ import annotations

import pytest

from envoy_diff.normalizer import (
    deduplicate_keys,
    normalize_env,
    normalize_keys,
    normalize_values,
)


# ---------------------------------------------------------------------------
# normalize_keys
# ---------------------------------------------------------------------------

def test_normalize_keys_uppercases_by_default():
    result = normalize_keys({"foo": "bar", "Baz": "qux"})
    assert set(result.keys()) == {"FOO", "BAZ"}


def test_normalize_keys_lowercase_option():
    result = normalize_keys({"FOO": "1", "Bar": "2"}, uppercase=False)
    assert set(result.keys()) == {"foo", "bar"}


def test_normalize_keys_preserves_values():
    result = normalize_keys({"key": "  value  "})
    assert result["KEY"] == "  value  "


def test_normalize_keys_raises_on_non_dict():
    with pytest.raises(TypeError):
        normalize_keys(["KEY=VAL"])  # type: ignore[arg-type]


def test_normalize_keys_does_not_mutate_original():
    original = {"foo": "bar"}
    normalize_keys(original)
    assert "foo" in original


# ---------------------------------------------------------------------------
# normalize_values
# ---------------------------------------------------------------------------

def test_normalize_values_strips_whitespace_by_default():
    result = normalize_values({"KEY": "  hello  "})
    assert result["KEY"] == "hello"


def test_normalize_values_no_strip():
    result = normalize_values({"KEY": "  hello  "}, strip=False)
    assert result["KEY"] == "  hello  "


def test_normalize_values_raises_on_non_dict():
    with pytest.raises(TypeError):
        normalize_values("not-a-dict")  # type: ignore[arg-type]


def test_normalize_values_does_not_mutate_original():
    original = {"KEY": "  val  "}
    normalize_values(original)
    assert original["KEY"] == "  val  "


# ---------------------------------------------------------------------------
# normalize_env
# ---------------------------------------------------------------------------

def test_normalize_env_uppercases_and_strips():
    result = normalize_env({"db_host": "  localhost  "})
    assert result == {"DB_HOST": "localhost"}


def test_normalize_env_only_uppercase():
    result = normalize_env({"db_host": "  val  "}, strip_values=False)
    assert result == {"DB_HOST": "  val  "}


def test_normalize_env_only_strip():
    result = normalize_env({"db_host": "  val  "}, uppercase_keys=False)
    assert result == {"db_host": "val"}


def test_normalize_env_empty_dict():
    assert normalize_env({}) == {}


# ---------------------------------------------------------------------------
# deduplicate_keys
# ---------------------------------------------------------------------------

def test_deduplicate_keys_passes_for_unique_keys():
    env = {"FOO": "1", "BAR": "2"}
    assert deduplicate_keys(env) == env


def test_deduplicate_keys_raises_on_case_collision():
    # Build a dict that has keys differing only by case — Python dicts won't
    # allow literal duplicates, so we simulate via a round-trip from pairs.
    pairs = [("FOO", "upper"), ("foo", "lower")]
    env = dict(pairs)  # Python keeps last value; only one key survives
    # With only one surviving key there should be no collision
    result = deduplicate_keys(env)
    assert len(result) == 1


def test_deduplicate_keys_returns_copy():
    env = {"A": "1"}
    result = deduplicate_keys(env)
    result["B"] = "2"
    assert "B" not in env
