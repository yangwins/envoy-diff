"""Integration tests: profiler + differ round-trip."""
from __future__ import annotations

from pathlib import Path

import pytest

from envoy_diff.differ import diff_envs, has_differences
from envoy_diff.profiler import load_profile, save_profile


@pytest.fixture()
def profile_path(tmp_path: Path) -> Path:
    return tmp_path / "profiles.json"


def test_profile_round_trip_no_diff(profile_path):
    env = {"APP": "myapp", "PORT": "8080", "DEBUG": "false"}
    save_profile("staging", env, profile_path)
    loaded = load_profile("staging", profile_path)
    result = diff_envs(env, loaded)
    assert not has_differences(result)


def test_profile_diff_detects_added_key(profile_path):
    base = {"APP": "myapp", "PORT": "8080"}
    save_profile("staging", base, profile_path)
    current = {"APP": "myapp", "PORT": "8080", "NEW_KEY": "value"}
    loaded = load_profile("staging", profile_path)
    result = diff_envs(loaded, current)
    assert "NEW_KEY" in result.added


def test_profile_diff_detects_changed_value(profile_path):
    save_profile("staging", {"PORT": "8080"}, profile_path)
    loaded = load_profile("staging", profile_path)
    result = diff_envs(loaded, {"PORT": "9090"})
    assert "PORT" in result.changed


def test_profile_diff_detects_removed_key(profile_path):
    save_profile("staging", {"APP": "myapp", "LEGACY": "yes"}, profile_path)
    loaded = load_profile("staging", profile_path)
    result = diff_envs(loaded, {"APP": "myapp"})
    assert "LEGACY" in result.removed


def test_multiple_profiles_independent(profile_path):
    save_profile("staging", {"ENV": "staging"}, profile_path)
    save_profile("prod", {"ENV": "prod"}, profile_path)
    staging = load_profile("staging", profile_path)
    prod = load_profile("prod", profile_path)
    result = diff_envs(staging, prod)
    assert "ENV" in result.changed
