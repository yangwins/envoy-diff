"""Unit tests for envoy_diff.transformer."""

from __future__ import annotations

import pytest

from envoy_diff.transformer import (
    rename_keys,
    strip_prefix,
    substitute_values,
    transform_env,
)


# ---------------------------------------------------------------------------
# strip_prefix
# ---------------------------------------------------------------------------

def test_strip_prefix_removes_matching_prefix():
    result = strip_prefix({"APP_HOST": "localhost", "APP_PORT": "8080"}, "APP_")
    assert result == {"HOST": "localhost", "PORT": "8080"}


def test_strip_prefix_leaves_non_matching_keys():
    result = strip_prefix({"APP_HOST": "a", "DB_URL": "b"}, "APP_")
    assert "DB_URL" in result
    assert "HOST" in result


def test_strip_prefix_empty_prefix_is_noop():
    env = {"KEY": "val"}
    assert strip_prefix(env, "") == env


def test_strip_prefix_does_not_mutate_original():
    env = {"APP_X": "1"}
    strip_prefix(env, "APP_")
    assert "APP_X" in env


def test_strip_prefix_raises_on_non_dict():
    with pytest.raises(TypeError):
        strip_prefix("not-a-dict", "APP_")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# rename_keys
# ---------------------------------------------------------------------------

def test_rename_keys_renames_specified_keys():
    result = rename_keys({"OLD_NAME": "v"}, {"OLD_NAME": "NEW_NAME"})
    assert result == {"NEW_NAME": "v"}


def test_rename_keys_leaves_unmapped_keys():
    result = rename_keys({"A": "1", "B": "2"}, {"A": "Z"})
    assert "B" in result
    assert result["B"] == "2"


def test_rename_keys_empty_mapping_is_noop():
    env = {"X": "y"}
    assert rename_keys(env, {}) == env


def test_rename_keys_raises_on_non_dict_env():
    with pytest.raises(TypeError):
        rename_keys([], {})  # type: ignore[arg-type]


def test_rename_keys_raises_on_non_dict_mapping():
    with pytest.raises(TypeError):
        rename_keys({}, "bad")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# substitute_values
# ---------------------------------------------------------------------------

def test_substitute_values_replaces_matching_value():
    result = substitute_values({"KEY": "<unset>"}, {"<unset>": ""})
    assert result == {"KEY": ""}


def test_substitute_values_leaves_non_matching_values():
    result = substitute_values({"KEY": "real"}, {"<unset>": ""})
    assert result == {"KEY": "real"}


def test_substitute_values_raises_on_non_dict():
    with pytest.raises(TypeError):
        substitute_values(None, {})  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# transform_env  (pipeline)
# ---------------------------------------------------------------------------

def test_transform_env_applies_all_steps():
    env = {"APP_HOST": "<unset>", "APP_PORT": "8080"}
    result = transform_env(
        env,
        strip_prefix_str="APP_",
        key_mapping={"HOST": "HOSTNAME"},
        value_substitutions={"<unset>": ""},
    )
    assert result == {"HOSTNAME": "", "PORT": "8080"}


def test_transform_env_no_args_is_copy():
    env = {"A": "1"}
    result = transform_env(env)
    assert result == env
    assert result is not env


def test_transform_env_does_not_mutate_original():
    env = {"APP_KEY": "val"}
    transform_env(env, strip_prefix_str="APP_")
    assert "APP_KEY" in env
