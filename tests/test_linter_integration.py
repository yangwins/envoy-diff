"""Integration tests: linter combined with differ, filter, and normalizer."""
from envoy_diff.linter import lint_env, lint_envs
from envoy_diff.differ import diff_envs
from envoy_diff.filter import filter_env
from envoy_diff.normalizer import normalize_keys


def test_lint_before_diff_catches_bad_keys_in_staging():
    staging = {"app_host": "staging.example.com", "DB_PORT": "5432"}
    production = {"APP_HOST": "prod.example.com", "DB_PORT": "5432"}
    lint_result = lint_env(staging)
    assert not lint_result.passed
    assert any(v.key == "app_host" for v in lint_result.violations)


def test_lint_passes_after_normalize_keys():
    env = {"app_host": "example.com", "db_port": "5432"}
    normalized = normalize_keys(env, uppercase=True)
    result = lint_env(normalized)
    assert result.passed


def test_lint_then_diff_workflow():
    """Lint both envs, then diff only if both pass."""
    env_a = {"APP_HOST": "staging.example.com", "PORT": "8080"}
    env_b = {"APP_HOST": "prod.example.com", "PORT": "8080"}
    lint_a = lint_env(env_a)
    lint_b = lint_env(env_b)
    assert lint_a.passed
    assert lint_b.passed
    diff = diff_envs(env_a, env_b)
    assert "APP_HOST" in diff.changed


def test_lint_combined_envs_reports_all_violations():
    env_a = {"bad-key": "1", "GOOD": "ok"}
    env_b = {"another_bad": "2", "GOOD": "ok"}
    result = lint_envs(env_a, env_b)
    keys = {v.key for v in result.violations}
    assert "bad-key" in keys
    assert "another_bad" in keys
    assert "GOOD" not in keys


def test_lint_after_filter_only_checks_included_keys():
    env = {"APP_HOST": "host", "bad-internal": "secret", "APP_PORT": "80"}
    filtered = filter_env(env, prefix="APP_")
    result = lint_env(filtered)
    assert result.passed
    assert all(v.key != "bad-internal" for v in result.violations)


def test_lint_result_as_dict_round_trips():
    env = {"bad-key": "v", "GOOD": "v"}
    result = lint_env(env)
    d = result.as_dict()
    assert d["passed"] is False
    assert d["violation_count"] == len(result.violations)
    assert d["violations"][0]["key"] == "bad-key"
