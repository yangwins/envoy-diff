"""Integration tests: filter → diff pipeline."""

from envoy_diff.filter import filter_env
from envoy_diff.differ import diff_envs, has_differences


STAGING = {
    "APP_HOST": "staging.example.com",
    "APP_PORT": "8080",
    "DB_HOST": "db-staging.internal",
    "DB_PASSWORD": "s3cr3t",
    "LOG_LEVEL": "DEBUG",
    "FEATURE_FLAG_X": "true",
}

PRODUCTION = {
    "APP_HOST": "prod.example.com",
    "APP_PORT": "443",
    "DB_HOST": "db-prod.internal",
    "DB_PASSWORD": "pr0ds3cr3t",
    "LOG_LEVEL": "INFO",
    "FEATURE_FLAG_X": "false",
}


def test_filter_then_diff_only_app_keys():
    a = filter_env(STAGING, prefix="APP_")
    b = filter_env(PRODUCTION, prefix="APP_")
    result = diff_envs(a, b)
    assert set(result.changed.keys()) == {"APP_HOST", "APP_PORT"}
    assert not result.added
    assert not result.removed


def test_filter_excludes_sensitive_then_diff():
    a = filter_env(STAGING, exclude=["*PASSWORD*", "*SECRET*"])
    b = filter_env(PRODUCTION, exclude=["*PASSWORD*", "*SECRET*"])
    result = diff_envs(a, b)
    assert "DB_PASSWORD" not in result.changed
    assert has_differences(result)  # other keys still differ


def test_filter_include_single_key_no_diff():
    # FEATURE_FLAG_X differs between envs
    a = filter_env(STAGING, include=["APP_HOST"])
    b = filter_env(PRODUCTION, include=["APP_HOST"])
    result = diff_envs(a, b)
    assert set(result.changed.keys()) == {"APP_HOST"}
    assert not result.added
    assert not result.removed


def test_filter_to_empty_set_no_differences():
    a = filter_env(STAGING, include=["NONEXISTENT_*"])
    b = filter_env(PRODUCTION, include=["NONEXISTENT_*"])
    result = diff_envs(a, b)
    assert not has_differences(result)


def test_filter_prefix_missing_in_one_env():
    # FEATURE_FLAG_X present in staging but not in a stripped production
    prod_stripped = {k: v for k, v in PRODUCTION.items() if not k.startswith("FEATURE")}
    a = filter_env(STAGING, prefix="FEATURE")
    b = filter_env(prod_stripped, prefix="FEATURE")
    result = diff_envs(a, b)
    assert "FEATURE_FLAG_X" in result.removed
