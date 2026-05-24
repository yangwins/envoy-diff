"""Integration tests: grouper combined with differ, filter, masker."""
from envoy_diff.differ import diff_envs
from envoy_diff.filter import filter_env
from envoy_diff.grouper import group_by_mapping, group_by_prefix
from envoy_diff.masker import mask_env


def test_group_prefix_after_real_diff():
    staging = {"APP_DEBUG": "true", "DB_HOST": "localhost", "DB_PORT": "5432"}
    production = {"APP_DEBUG": "false", "DB_HOST": "prod-db", "DB_PORT": "5432"}
    result = diff_envs(staging, production)
    gd = group_by_prefix(result, ["APP", "DB"])
    assert "APP_DEBUG" in gd.groups["APP"]
    assert "DB_HOST" in gd.groups["DB"]
    assert "DB_PORT" not in gd.groups["DB"]  # unchanged, excluded by default


def test_group_prefix_include_unchanged_after_diff():
    staging = {"APP_DEBUG": "true", "DB_PORT": "5432"}
    production = {"APP_DEBUG": "false", "DB_PORT": "5432"}
    result = diff_envs(staging, production)
    gd = group_by_prefix(result, ["DB"], include_unchanged=True)
    assert "DB_PORT" in gd.groups["DB"]


def test_group_after_filter_limits_scope():
    staging = {"APP_HOST": "a", "APP_PORT": "80", "REDIS_URL": "r1"}
    production = {"APP_HOST": "b", "APP_PORT": "80", "REDIS_URL": "r2"}
    filtered_s = filter_env(staging, prefix="APP")
    filtered_p = filter_env(production, prefix="APP")
    result = diff_envs(filtered_s, filtered_p)
    gd = group_by_prefix(result, ["APP", "REDIS"])
    assert gd.groups["REDIS"] == []
    assert "APP_HOST" in gd.groups["APP"]


def test_group_mapping_after_mask_hides_values_not_keys():
    staging = {"DB_PASSWORD": "hunter2", "APP_NAME": "myapp"}
    production = {"DB_PASSWORD": "s3cr3t", "APP_NAME": "myapp"}
    result = diff_envs(mask_env(staging), mask_env(production))
    gd = group_by_mapping(
        result, {"database": ["DB_PASSWORD"], "app": ["APP_NAME"]}
    )
    # Key is still grouped even though value is masked
    assert "DB_PASSWORD" in gd.groups["database"]


def test_ungrouped_keys_are_not_lost():
    staging = {"APP_X": "1", "ORPHAN": "old"}
    production = {"APP_X": "2", "ORPHAN": "new"}
    result = diff_envs(staging, production)
    gd = group_by_prefix(result, ["APP"])
    assert "ORPHAN" in gd.ungrouped


def test_group_as_dict_round_trips():
    staging = {"APP_DEBUG": "1"}
    production = {"APP_DEBUG": "0"}
    result = diff_envs(staging, production)
    gd = group_by_prefix(result, ["APP"])
    d = gd.as_dict()
    assert isinstance(d["groups"], dict)
    assert isinstance(d["ungrouped"], list)
    assert "APP_DEBUG" in d["groups"]["APP"]
