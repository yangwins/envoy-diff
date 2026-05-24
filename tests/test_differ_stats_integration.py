"""Integration tests: differ_stats composed with differ, filter, and masker."""

from __future__ import annotations

from envoy_diff.differ import diff_envs
from envoy_diff.differ_stats import compute_stats, format_stats
from envoy_diff.filter import filter_env
from envoy_diff.masker import mask_env


def test_stats_from_real_diff_correct_counts():
    staging = {"APP_HOST": "staging.example.com", "APP_PORT": "8080", "DB_URL": "postgres://staging"}
    prod = {"APP_HOST": "prod.example.com", "APP_PORT": "8080", "NEW_KEY": "value"}
    result = diff_envs(staging, prod)
    stats = compute_stats(result)
    assert stats.changed == 1   # APP_HOST
    assert stats.added == 1     # NEW_KEY
    assert stats.removed == 1   # DB_URL
    assert stats.unchanged == 1 # APP_PORT
    assert stats.total_keys == 4


def test_stats_change_rate_reflects_real_diff():
    staging = {"A": "1", "B": "2", "C": "3", "D": "4"}
    prod    = {"A": "1", "B": "changed", "C": "3", "E": "new"}
    result = diff_envs(staging, prod)
    stats = compute_stats(result)
    # changed=B, added=E, removed=D => 3 out of 5 total
    assert stats.total_keys == 5
    assert abs(stats.change_rate - 3 / 5) < 1e-6


def test_stats_after_filter_limits_scope():
    staging = {"APP_HOST": "s", "DB_URL": "db-s", "CACHE_URL": "c-s"}
    prod    = {"APP_HOST": "p", "DB_URL": "db-p", "CACHE_URL": "c-p"}
    filtered_staging = filter_env(staging, prefix="APP")
    filtered_prod    = filter_env(prod,    prefix="APP")
    result = diff_envs(filtered_staging, filtered_prod)
    stats = compute_stats(result)
    assert stats.total_keys == 1
    assert stats.changed == 1


def test_stats_top_changed_keys_after_mask_does_not_affect_keys():
    staging = {"SECRET_KEY": "abc", "APP_ENV": "staging"}
    prod    = {"SECRET_KEY": "xyz", "APP_ENV": "prod"}
    masked_staging = mask_env(staging)
    masked_prod    = mask_env(prod)
    result = diff_envs(masked_staging, masked_prod)
    stats = compute_stats(result)
    # Keys should still appear even though values are masked
    assert "SECRET_KEY" in stats.top_changed_keys or "APP_ENV" in stats.top_changed_keys


def test_stats_empty_envs_zero_rate():
    result = diff_envs({}, {})
    stats = compute_stats(result)
    assert stats.total_keys == 0
    assert stats.change_rate == 0.0


def test_format_stats_integration_returns_multiline():
    staging = {"X": "1", "Y": "2"}
    prod    = {"X": "changed", "Z": "new"}
    result = diff_envs(staging, prod)
    output = format_stats(compute_stats(result))
    lines = output.strip().splitlines()
    assert len(lines) >= 6
