"""Tests for envoy_diff.sorter."""

from __future__ import annotations

import pytest

from envoy_diff.differ import DiffResult
from envoy_diff.sorter import SortOrder, sort_diff_result, sort_orders


def _make_result() -> DiffResult:
    return DiffResult(
        changed={"ZEBRA_URL": {"status": "changed", "old": "a", "new": "b"}, "APP_HOST": {"status": "changed", "old": "x", "new": "y"}},
        added={"NEW_FLAG": {"status": "added", "new": "1"}, "ALPHA_VAR": {"status": "added", "new": "2"}},
        removed={"OLD_KEY": {"status": "removed", "old": "gone"}, "BETA_KEY": {"status": "removed", "old": "bye"}},
        unchanged={"PORT": {"status": "unchanged", "value": "8080"}, "DEBUG": {"status": "unchanged", "value": "false"}},
    )


def test_sort_orders_returns_list():
    orders = sort_orders()
    assert isinstance(orders, list)
    assert "key" in orders
    assert "status" in orders
    assert "none" in orders


def test_sort_by_key_changed_is_alphabetical():
    result = sort_diff_result(_make_result(), SortOrder.KEY)
    keys = list(result["changed"].keys())
    assert keys == sorted(keys, key=str.lower)


def test_sort_by_key_added_is_alphabetical():
    result = sort_diff_result(_make_result(), SortOrder.KEY)
    keys = list(result["added"].keys())
    assert keys == sorted(keys, key=str.lower)


def test_sort_by_key_removed_is_alphabetical():
    result = sort_diff_result(_make_result(), SortOrder.KEY)
    keys = list(result["removed"].keys())
    assert keys == sorted(keys, key=str.lower)


def test_sort_by_key_unchanged_is_alphabetical():
    result = sort_diff_result(_make_result(), SortOrder.KEY)
    keys = list(result["unchanged"].keys())
    assert keys == sorted(keys, key=str.lower)


def test_sort_none_preserves_insertion_order():
    original = _make_result()
    result = sort_diff_result(original, SortOrder.NONE)
    assert list(result["changed"].keys()) == list(original["changed"].keys())
    assert list(result["added"].keys()) == list(original["added"].keys())


def test_sort_does_not_mutate_original():
    original = _make_result()
    original_changed_keys = list(original["changed"].keys())
    sort_diff_result(original, SortOrder.KEY)
    assert list(original["changed"].keys()) == original_changed_keys


def test_sort_returns_diff_result_type():
    result = sort_diff_result(_make_result(), SortOrder.KEY)
    assert isinstance(result, dict)
    assert "changed" in result
    assert "added" in result
    assert "removed" in result
    assert "unchanged" in result


def test_sort_by_key_default_is_key_order():
    result_default = sort_diff_result(_make_result())
    result_key = sort_diff_result(_make_result(), SortOrder.KEY)
    assert list(result_default["changed"].keys()) == list(result_key["changed"].keys())


def test_sort_status_enum_values():
    assert SortOrder.KEY.value == "key"
    assert SortOrder.STATUS.value == "status"
    assert SortOrder.NONE.value == "none"
