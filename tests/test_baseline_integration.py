"""Integration tests: baseline -> diff workflow."""

from __future__ import annotations

from pathlib import Path

from envoy_diff.baseline import save_baseline, load_baseline
from envoy_diff.differ import diff_envs


STAGING: dict[str, str] = {
    "APP_ENV": "staging",
    "DB_HOST": "db.staging.local",
    "FEATURE_X": "true",
}

PRODUCTION: dict[str, str] = {
    "APP_ENV": "production",
    "DB_HOST": "db.prod.local",
    "NEW_RELIC_KEY": "abc123",
}


def test_baseline_diff_no_changes(tmp_path):
    bl = tmp_path / "baseline.json"
    save_baseline(STAGING, path=bl)
    loaded = load_baseline(path=bl)
    result = diff_envs(STAGING, loaded)
    assert not result.added
    assert not result.removed
    assert not result.changed


def test_baseline_diff_detects_added_key(tmp_path):
    bl = tmp_path / "baseline.json"
    save_baseline(STAGING, path=bl)
    current = {**STAGING, "NEW_KEY": "hello"}
    loaded = load_baseline(path=bl)
    result = diff_envs(loaded, current)
    assert "NEW_KEY" in result.added


def test_baseline_diff_detects_removed_key(tmp_path):
    bl = tmp_path / "baseline.json"
    save_baseline(STAGING, path=bl)
    current = {k: v for k, v in STAGING.items() if k != "FEATURE_X"}
    loaded = load_baseline(path=bl)
    result = diff_envs(loaded, current)
    assert "FEATURE_X" in result.removed


def test_baseline_diff_detects_changed_value(tmp_path):
    bl = tmp_path / "baseline.json"
    save_baseline(STAGING, path=bl)
    current = {**STAGING, "DB_HOST": "db.new.local"}
    loaded = load_baseline(path=bl)
    result = diff_envs(loaded, current)
    assert "DB_HOST" in result.changed


def test_baseline_vs_production(tmp_path):
    bl = tmp_path / "baseline.json"
    save_baseline(STAGING, path=bl)
    loaded = load_baseline(path=bl)
    result = diff_envs(loaded, PRODUCTION)
    assert "NEW_RELIC_KEY" in result.added
    assert "FEATURE_X" in result.removed
    assert "APP_ENV" in result.changed
    assert "DB_HOST" in result.changed
