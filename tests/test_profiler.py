"""Unit tests for envoy_diff.profiler."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envoy_diff.profiler import (
    delete_profile,
    list_profiles,
    load_profile,
    save_profile,
)


@pytest.fixture()
def profile_path(tmp_path: Path) -> Path:
    return tmp_path / "profiles.json"


def test_list_profiles_empty_when_no_file(profile_path):
    assert list_profiles(profile_path) == []


def test_save_profile_creates_file(profile_path):
    save_profile("staging", {"FOO": "bar"}, profile_path)
    assert profile_path.exists()


def test_save_profile_stores_env(profile_path):
    save_profile("staging", {"FOO": "bar", "BAZ": "qux"}, profile_path)
    data = json.loads(profile_path.read_text())
    assert data["staging"] == {"FOO": "bar", "BAZ": "qux"}


def test_save_profile_coerces_values_to_str(profile_path):
    save_profile("prod", {"PORT": 8080}, profile_path)  # type: ignore[dict-item]
    data = json.loads(profile_path.read_text())
    assert data["prod"]["PORT"] == "8080"


def test_list_profiles_returns_sorted_names(profile_path):
    save_profile("prod", {"A": "1"}, profile_path)
    save_profile("staging", {"A": "2"}, profile_path)
    save_profile("dev", {"A": "3"}, profile_path)
    assert list_profiles(profile_path) == ["dev", "prod", "staging"]


def test_load_profile_returns_env(profile_path):
    save_profile("staging", {"X": "hello"}, profile_path)
    env = load_profile("staging", profile_path)
    assert env == {"X": "hello"}


def test_load_profile_raises_on_missing(profile_path):
    with pytest.raises(KeyError, match="not found"):
        load_profile("ghost", profile_path)


def test_delete_profile_returns_true_when_existed(profile_path):
    save_profile("staging", {"A": "1"}, profile_path)
    assert delete_profile("staging", profile_path) is True


def test_delete_profile_removes_entry(profile_path):
    save_profile("staging", {"A": "1"}, profile_path)
    delete_profile("staging", profile_path)
    assert "staging" not in list_profiles(profile_path)


def test_delete_profile_returns_false_when_missing(profile_path):
    assert delete_profile("nonexistent", profile_path) is False


def test_save_profile_raises_on_empty_name(profile_path):
    with pytest.raises(ValueError, match="empty"):
        save_profile("", {"A": "1"}, profile_path)


def test_save_profile_overwrites_existing(profile_path):
    save_profile("staging", {"A": "1"}, profile_path)
    save_profile("staging", {"A": "99"}, profile_path)
    env = load_profile("staging", profile_path)
    assert env["A"] == "99"
