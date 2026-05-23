"""Unit tests for envoy_diff.merger."""

import pytest

from envoy_diff.merger import (
    MergeConflictError,
    MergeStrategy,
    merge_envs,
    merge_strategies,
)


def test_merge_strategies_returns_list():
    assert isinstance(merge_strategies, list)
    assert "left" in merge_strategies
    assert "right" in merge_strategies
    assert "strict" in merge_strategies


def test_merge_envs_right_wins_by_default():
    left = {"A": "1", "B": "2"}
    right = {"B": "99", "C": "3"}
    result = merge_envs(left, right)
    assert result == {"A": "1", "B": "99", "C": "3"}


def test_merge_envs_left_strategy_keeps_left_on_conflict():
    left = {"A": "1", "B": "original"}
    right = {"B": "override", "C": "new"}
    result = merge_envs(left, right, strategy=MergeStrategy.LEFT)
    assert result["B"] == "original"
    assert result["C"] == "new"


def test_merge_envs_strict_raises_on_conflict():
    left = {"KEY": "val1"}
    right = {"KEY": "val2"}
    with pytest.raises(MergeConflictError) as exc_info:
        merge_envs(left, right, strategy=MergeStrategy.STRICT)
    assert exc_info.value.key == "KEY"
    assert exc_info.value.left_val == "val1"
    assert exc_info.value.right_val == "val2"


def test_merge_envs_strict_passes_when_values_identical():
    left = {"KEY": "same"}
    right = {"KEY": "same", "EXTRA": "extra"}
    result = merge_envs(left, right, strategy=MergeStrategy.STRICT)
    assert result["KEY"] == "same"
    assert result["EXTRA"] == "extra"


def test_merge_envs_does_not_mutate_left():
    left = {"A": "1"}
    right = {"A": "2"}
    merge_envs(left, right)
    assert left["A"] == "1"


def test_merge_envs_does_not_mutate_right():
    left = {"A": "1"}
    right = {"B": "2"}
    merge_envs(left, right)
    assert right == {"B": "2"}


def test_merge_envs_empty_right_returns_copy_of_left():
    left = {"A": "1", "B": "2"}
    result = merge_envs(left, {})
    assert result == left
    assert result is not left


def test_merge_envs_empty_left_returns_copy_of_right():
    right = {"A": "1", "B": "2"}
    result = merge_envs({}, right)
    assert result == right


def test_merge_envs_coerces_values_to_str():
    left = {"PORT": 8080}  # type: ignore[dict-item]
    right = {"DEBUG": True}  # type: ignore[dict-item]
    result = merge_envs(left, right)  # type: ignore[arg-type]
    assert result["PORT"] == "8080"
    assert result["DEBUG"] == "True"


def test_merge_envs_raises_on_non_dict_left():
    with pytest.raises(TypeError):
        merge_envs("not-a-dict", {})  # type: ignore[arg-type]


def test_merge_envs_raises_on_non_dict_right():
    with pytest.raises(TypeError):
        merge_envs({}, ["list"])  # type: ignore[arg-type]


def test_merge_envs_prefix_filters_right_keys():
    left = {"APP_HOST": "localhost"}
    right = {"APP_PORT": "9000", "DB_HOST": "db-server"}
    result = merge_envs(left, right, prefix="APP_")
    assert "APP_PORT" in result
    assert "DB_HOST" not in result


def test_merge_conflict_error_message_contains_key():
    err = MergeConflictError("MY_KEY", "old", "new")
    assert "MY_KEY" in str(err)
    assert "old" in str(err)
    assert "new" in str(err)
