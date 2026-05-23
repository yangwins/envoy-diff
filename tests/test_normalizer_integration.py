"""Integration tests: normalizer combined with differ and filter."""

from __future__ import annotations

from envoy_diff.differ import diff_envs
from envoy_diff.filter import filter_env
from envoy_diff.normalizer import normalize_env


def test_normalize_then_diff_detects_no_change_after_case_fix():
    staging = {"db_host": "localhost"}
    production = {"DB_HOST": "localhost"}
    norm_s = normalize_env(staging)
    norm_p = normalize_env(production)
    result = diff_envs(norm_s, norm_p)
    assert result.changed == {}
    assert result.added == {}
    assert result.removed == {}


def test_normalize_then_diff_detects_value_change_after_strip():
    staging = {"API_URL": "  https://staging.example.com  "}
    production = {"API_URL": "https://production.example.com"}
    norm_s = normalize_env(staging)
    norm_p = normalize_env(production)
    result = diff_envs(norm_s, norm_p)
    assert "API_URL" in result.changed


def test_normalize_strips_whitespace_so_values_match():
    staging = {"TIMEOUT": "  30  "}
    production = {"TIMEOUT": "30"}
    norm_s = normalize_env(staging)
    norm_p = normalize_env(production)
    result = diff_envs(norm_s, norm_p)
    assert result.changed == {}


def test_normalize_then_filter_then_diff():
    staging = {"app_host": "s.example.com", "db_pass": "secret"}
    production = {"APP_HOST": "p.example.com", "DB_PASS": "secret"}
    norm_s = normalize_env(staging)
    norm_p = normalize_env(production)
    filtered_s = filter_env(norm_s, prefix="APP_")
    filtered_p = filter_env(norm_p, prefix="APP_")
    result = diff_envs(filtered_s, filtered_p)
    assert "APP_HOST" in result.changed
    assert "DB_PASS" not in result.changed


def test_normalize_empty_envs_produces_empty_diff():
    result = diff_envs(normalize_env({}), normalize_env({}))
    assert result.added == {}
    assert result.removed == {}
    assert result.changed == {}
