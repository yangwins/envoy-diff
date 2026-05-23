"""Integration tests: snapshotter wired with loader and differ."""

from __future__ import annotations

from envoy_diff.differ import diff_envs, has_differences
from envoy_diff.loader import load_from_dict
from envoy_diff.snapshotter import load_snapshot, save_snapshot


def test_round_trip_preserves_env(tmp_path):
    """save then load returns an identical mapping."""
    original = {"APP_PORT": "8080", "DB_HOST": "localhost", "DEBUG": "true"}
    dest = tmp_path / "snap.json"
    save_snapshot(original, dest)
    restored = load_snapshot(dest)
    assert restored == original


def test_snapshot_diff_detects_no_changes(tmp_path):
    """Diffing two snapshots of the same env yields no differences."""
    env = {"FOO": "1", "BAR": "2"}
    snap1 = tmp_path / "a.json"
    snap2 = tmp_path / "b.json"
    save_snapshot(env, snap1)
    save_snapshot(env, snap2)
    result = diff_envs(load_snapshot(snap1), load_snapshot(snap2))
    assert not has_differences(result)


def test_snapshot_diff_detects_added_key(tmp_path):
    base = {"FOO": "1"}
    updated = {"FOO": "1", "NEW_KEY": "hello"}
    snap1 = tmp_path / "base.json"
    snap2 = tmp_path / "updated.json"
    save_snapshot(base, snap1)
    save_snapshot(updated, snap2)
    result = diff_envs(load_snapshot(snap1), load_snapshot(snap2))
    assert "NEW_KEY" in result.added


def test_snapshot_diff_detects_changed_value(tmp_path):
    snap1 = tmp_path / "old.json"
    snap2 = tmp_path / "new.json"
    save_snapshot({"VERSION": "1.0"}, snap1)
    save_snapshot({"VERSION": "2.0"}, snap2)
    result = diff_envs(load_snapshot(snap1), load_snapshot(snap2))
    assert "VERSION" in result.changed


def test_snapshot_diff_detects_removed_key(tmp_path):
    snap1 = tmp_path / "old.json"
    snap2 = tmp_path / "new.json"
    save_snapshot({"GONE": "yes", "KEEP": "ok"}, snap1)
    save_snapshot({"KEEP": "ok"}, snap2)
    result = diff_envs(load_snapshot(snap1), load_snapshot(snap2))
    assert "GONE" in result.removed


def test_load_from_dict_then_snapshot_round_trip(tmp_path):
    """load_from_dict + save_snapshot + load_snapshot stays consistent."""
    raw = {"PORT": 9000, "WORKERS": 4}
    env = load_from_dict(raw)
    dest = tmp_path / "snap.json"
    save_snapshot(env, dest)
    restored = load_snapshot(dest)
    assert restored == {"PORT": "9000", "WORKERS": "4"}
