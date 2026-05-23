"""Tests for envoy_diff.ignorer."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envoy_diff.ignorer import (
    _ignore_path,
    add_ignored_key,
    apply_ignore,
    clear_ignored_keys,
    load_ignored_keys,
    remove_ignored_key,
)


@pytest.fixture()
def ig_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_ignore_path_default_is_cwd():
    p = _ignore_path()
    assert p.name == ".envoy_ignore.json"
    assert p.parent == Path(".")


def test_ignore_path_custom_directory(ig_dir):
    p = _ignore_path(ig_dir)
    assert p == ig_dir / ".envoy_ignore.json"


def test_load_ignored_keys_empty_when_no_file(ig_dir):
    assert load_ignored_keys(ig_dir) == []


def test_add_ignored_key_creates_file(ig_dir):
    add_ignored_key("SECRET", ig_dir)
    assert (ig_dir / ".envoy_ignore.json").exists()


def test_add_ignored_key_returns_sorted_list(ig_dir):
    add_ignored_key("ZEBRA", ig_dir)
    result = add_ignored_key("ALPHA", ig_dir)
    assert result == ["ALPHA", "ZEBRA"]


def test_add_ignored_key_is_idempotent(ig_dir):
    add_ignored_key("KEY", ig_dir)
    result = add_ignored_key("KEY", ig_dir)
    assert result.count("KEY") == 1


def test_load_ignored_keys_returns_persisted_keys(ig_dir):
    add_ignored_key("FOO", ig_dir)
    add_ignored_key("BAR", ig_dir)
    keys = load_ignored_keys(ig_dir)
    assert "FOO" in keys
    assert "BAR" in keys


def test_remove_ignored_key_removes_entry(ig_dir):
    add_ignored_key("FOO", ig_dir)
    add_ignored_key("BAR", ig_dir)
    result = remove_ignored_key("FOO", ig_dir)
    assert "FOO" not in result
    assert "BAR" in result


def test_remove_ignored_key_nonexistent_is_noop(ig_dir):
    add_ignored_key("ONLY", ig_dir)
    result = remove_ignored_key("MISSING", ig_dir)
    assert result == ["ONLY"]


def test_apply_ignore_removes_ignored_keys(ig_dir):
    add_ignored_key("SECRET", ig_dir)
    env = {"SECRET": "abc", "PORT": "8080"}
    result = apply_ignore(env, ig_dir)
    assert "SECRET" not in result
    assert result["PORT"] == "8080"


def test_apply_ignore_does_not_mutate_original(ig_dir):
    add_ignored_key("X", ig_dir)
    env = {"X": "1", "Y": "2"}
    apply_ignore(env, ig_dir)
    assert "X" in env


def test_apply_ignore_no_file_returns_full_env(ig_dir):
    env = {"A": "1", "B": "2"}
    assert apply_ignore(env, ig_dir) == env


def test_clear_ignored_keys_removes_file(ig_dir):
    add_ignored_key("FOO", ig_dir)
    clear_ignored_keys(ig_dir)
    assert not (ig_dir / ".envoy_ignore.json").exists()


def test_clear_ignored_keys_noop_when_no_file(ig_dir):
    clear_ignored_keys(ig_dir)  # should not raise


def test_load_ignored_keys_raises_on_invalid_json(ig_dir):
    p = ig_dir / ".envoy_ignore.json"
    p.write_text(json.dumps({"key": "not-a-list"}), encoding="utf-8")
    with pytest.raises(ValueError, match="JSON array"):
        load_ignored_keys(ig_dir)
