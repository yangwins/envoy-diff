"""Unit tests for envoy_diff.grouper."""
import pytest

from envoy_diff.differ import DiffResult
from envoy_diff.grouper import GroupedDiff, group_by_mapping, group_by_prefix


def _make_result(
    added=(), removed=(), changed=(), unchanged=()
) -> DiffResult:
    return DiffResult(
        added=dict.fromkeys(added, "v"),
        removed=dict.fromkeys(removed, "v"),
        changed={k: ("old", "new") for k in changed},
        unchanged=dict.fromkeys(unchanged, "v"),
    )


# ---------------------------------------------------------------------------
# GroupedDiff helpers
# ---------------------------------------------------------------------------

def test_grouped_diff_all_keys_combines_groups():
    gd = GroupedDiff(groups={"A": ["K1", "K2"], "B": ["K3"]}, ungrouped=[])
    assert sorted(gd.all_keys()) == ["K1", "K2", "K3"]


def test_grouped_diff_as_dict_sorts_keys():
    gd = GroupedDiff(groups={"A": ["Z", "A"]}, ungrouped=["M"])
    d = gd.as_dict()
    assert d["groups"]["A"] == ["A", "Z"]
    assert d["ungrouped"] == ["M"]


# ---------------------------------------------------------------------------
# group_by_prefix
# ---------------------------------------------------------------------------

def test_group_by_prefix_assigns_added_key():
    result = _make_result(added=["APP_DEBUG"])
    gd = group_by_prefix(result, ["APP"])
    assert "APP_DEBUG" in gd.groups["APP"]


def test_group_by_prefix_assigns_removed_key():
    result = _make_result(removed=["DB_HOST"])
    gd = group_by_prefix(result, ["DB"])
    assert "DB_HOST" in gd.groups["DB"]


def test_group_by_prefix_assigns_changed_key():
    result = _make_result(changed=["DB_PORT"])
    gd = group_by_prefix(result, ["DB"])
    assert "DB_PORT" in gd.groups["DB"]


def test_group_by_prefix_unmatched_goes_to_ungrouped():
    result = _make_result(added=["REDIS_URL"])
    gd = group_by_prefix(result, ["APP", "DB"])
    assert "REDIS_URL" in gd.ungrouped


def test_group_by_prefix_longest_prefix_wins():
    result = _make_result(added=["APP_API_KEY"])
    gd = group_by_prefix(result, ["APP", "APP_API"])
    assert "APP_API_KEY" in gd.groups["APP_API"]
    assert "APP_API_KEY" not in gd.groups["APP"]


def test_group_by_prefix_case_insensitive_match():
    result = _make_result(added=["app_debug"])
    gd = group_by_prefix(result, ["APP"])
    assert "app_debug" in gd.groups["APP"]


def test_group_by_prefix_unchanged_excluded_by_default():
    result = _make_result(unchanged=["APP_VERSION"])
    gd = group_by_prefix(result, ["APP"])
    assert "APP_VERSION" not in gd.groups["APP"]
    assert "APP_VERSION" not in gd.ungrouped


def test_group_by_prefix_include_unchanged_flag():
    result = _make_result(unchanged=["APP_VERSION"])
    gd = group_by_prefix(result, ["APP"], include_unchanged=True)
    assert "APP_VERSION" in gd.groups["APP"]


def test_group_by_prefix_empty_result_empty_groups():
    result = _make_result()
    gd = group_by_prefix(result, ["APP", "DB"])
    assert gd.groups == {"APP": [], "DB": []}
    assert gd.ungrouped == []


# ---------------------------------------------------------------------------
# group_by_mapping
# ---------------------------------------------------------------------------

def test_group_by_mapping_places_key_in_declared_group():
    result = _make_result(added=["SECRET_KEY"])
    gd = group_by_mapping(result, {"secrets": ["SECRET_KEY"]})
    assert "SECRET_KEY" in gd.groups["secrets"]


def test_group_by_mapping_unmapped_key_is_ungrouped():
    result = _make_result(added=["UNKNOWN_VAR"])
    gd = group_by_mapping(result, {"secrets": ["SECRET_KEY"]})
    assert "UNKNOWN_VAR" in gd.ungrouped


def test_group_by_mapping_multiple_groups():
    result = _make_result(added=["DB_HOST", "APP_PORT"])
    gd = group_by_mapping(
        result,
        {"database": ["DB_HOST"], "app": ["APP_PORT"]},
    )
    assert "DB_HOST" in gd.groups["database"]
    assert "APP_PORT" in gd.groups["app"]


def test_group_by_mapping_unchanged_excluded_by_default():
    result = _make_result(unchanged=["APP_PORT"])
    gd = group_by_mapping(result, {"app": ["APP_PORT"]})
    assert "APP_PORT" not in gd.groups["app"]


def test_group_by_mapping_include_unchanged():
    result = _make_result(unchanged=["APP_PORT"])
    gd = group_by_mapping(result, {"app": ["APP_PORT"]}, include_unchanged=True)
    assert "APP_PORT" in gd.groups["app"]
