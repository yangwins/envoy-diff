"""Tests for envoy_diff.snapshotter."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envoy_diff.snapshotter import (
    load_snapshot,
    save_snapshot,
    snapshot_metadata,
)


# ---------------------------------------------------------------------------
# save_snapshot
# ---------------------------------------------------------------------------

def test_save_snapshot_creates_file(tmp_path):
    dest = tmp_path / "snap.json"
    result = save_snapshot({"A": "1"}, dest)
    assert result.exists()


def test_save_snapshot_returns_resolved_path(tmp_path):
    dest = tmp_path / "snap.json"
    result = save_snapshot({}, dest)
    assert result == dest.resolve()


def test_save_snapshot_writes_env_keys(tmp_path):
    env = {"FOO": "bar", "BAZ": "qux"}
    dest = tmp_path / "snap.json"
    save_snapshot(env, dest)
    payload = json.loads(dest.read_text())
    assert payload["env"] == env


def test_save_snapshot_includes_metadata(tmp_path):
    dest = tmp_path / "snap.json"
    save_snapshot({"X": "y"}, dest, label="staging")
    payload = json.loads(dest.read_text())
    assert payload["meta"]["label"] == "staging"
    assert payload["meta"]["key_count"] == 1
    assert "created_at" in payload["meta"]


def test_save_snapshot_raises_on_existing_file(tmp_path):
    dest = tmp_path / "snap.json"
    save_snapshot({}, dest)
    with pytest.raises(FileExistsError):
        save_snapshot({}, dest)


def test_save_snapshot_overwrite_flag(tmp_path):
    dest = tmp_path / "snap.json"
    save_snapshot({"A": "1"}, dest)
    save_snapshot({"A": "2"}, dest, overwrite=True)
    payload = json.loads(dest.read_text())
    assert payload["env"]["A"] == "2"


def test_save_snapshot_raises_on_non_json_extension(tmp_path):
    with pytest.raises(ValueError, match=".json"):
        save_snapshot({}, tmp_path / "snap.txt")


def test_save_snapshot_creates_parent_dirs(tmp_path):
    dest = tmp_path / "nested" / "dir" / "snap.json"
    save_snapshot({}, dest)
    assert dest.exists()


# ---------------------------------------------------------------------------
# load_snapshot
# ---------------------------------------------------------------------------

def test_load_snapshot_returns_dict(tmp_path):
    dest = tmp_path / "snap.json"
    save_snapshot({"KEY": "val"}, dest)
    env = load_snapshot(dest)
    assert env == {"KEY": "val"}


def test_load_snapshot_coerces_values_to_str(tmp_path):
    dest = tmp_path / "snap.json"
    payload = {"meta": {}, "env": {"NUM": 42}}
    dest.write_text(json.dumps(payload))
    env = load_snapshot(dest)
    assert env["NUM"] == "42"


def test_load_snapshot_raises_on_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_snapshot(tmp_path / "ghost.json")


def test_load_snapshot_raises_on_invalid_json(tmp_path):
    dest = tmp_path / "bad.json"
    dest.write_text("not json")
    with pytest.raises(ValueError, match="Invalid JSON"):
        load_snapshot(dest)


def test_load_snapshot_raises_on_missing_env_key(tmp_path):
    dest = tmp_path / "bad.json"
    dest.write_text(json.dumps({"meta": {}}))
    with pytest.raises(ValueError, match="'env'"):
        load_snapshot(dest)


# ---------------------------------------------------------------------------
# snapshot_metadata
# ---------------------------------------------------------------------------

def test_snapshot_metadata_returns_meta_block(tmp_path):
    dest = tmp_path / "snap.json"
    save_snapshot({"A": "1", "B": "2"}, dest, label="prod")
    meta = snapshot_metadata(dest)
    assert meta["label"] == "prod"
    assert meta["key_count"] == 2


def test_snapshot_metadata_raises_on_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        snapshot_metadata(tmp_path / "ghost.json")
