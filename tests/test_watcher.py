"""Tests for envoy_diff.watcher."""

from __future__ import annotations

import time
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from envoy_diff.watcher import WatchEvent, watch
from envoy_diff.differ import diff_envs


# ---------------------------------------------------------------------------
# WatchEvent
# ---------------------------------------------------------------------------

def _make_event(cycle: int = 1, added: dict | None = None) -> WatchEvent:
    base = {"KEY": "value"}
    other = {**base, **(added or {})}
    result = diff_envs(base, other)
    return WatchEvent(cycle=cycle, result=result, previous_snapshot=Path("/tmp/snap.json"))


def test_watch_event_has_changes_true_when_diff():
    event = _make_event(added={"NEW": "1"})
    assert event.has_changes is True


def test_watch_event_has_changes_false_when_identical():
    event = _make_event()
    assert event.has_changes is False


def test_watch_event_stores_cycle():
    event = _make_event(cycle=7)
    assert event.cycle == 7


def test_watch_event_timestamp_is_float():
    event = _make_event()
    assert isinstance(event.timestamp, float)


# ---------------------------------------------------------------------------
# watch() function
# ---------------------------------------------------------------------------

def test_watch_calls_on_cycle(tmp_path):
    cycles_seen = []

    env_sequence = [
        {"A": "1"},  # baseline
        {"A": "1"},  # cycle 1 — no change
        {"A": "2"},  # cycle 2 — change
    ]
    env_iter = iter(env_sequence)

    with patch("envoy_diff.watcher.load_from_env", side_effect=lambda: next(env_iter)), \
         patch("envoy_diff.watcher.time.sleep"):
        watch(
            snapshot_dir=tmp_path,
            interval=0,
            max_cycles=2,
            on_cycle=cycles_seen.append,
        )

    assert cycles_seen == [1, 2]


def test_watch_calls_on_change_only_when_diff(tmp_path):
    events = []

    env_sequence = [
        {"A": "1"},  # baseline
        {"A": "1"},  # cycle 1 — no change
        {"A": "2"},  # cycle 2 — change
    ]
    env_iter = iter(env_sequence)

    with patch("envoy_diff.watcher.load_from_env", side_effect=lambda: next(env_iter)), \
         patch("envoy_diff.watcher.time.sleep"):
        watch(
            snapshot_dir=tmp_path,
            interval=0,
            max_cycles=2,
            on_change=events.append,
        )

    assert len(events) == 1
    assert events[0].cycle == 2
    assert events[0].has_changes is True


def test_watch_creates_snapshot_dir(tmp_path):
    new_dir = tmp_path / "deep" / "snapshots"
    env_iter = iter([{"X": "1"}])

    with patch("envoy_diff.watcher.load_from_env", side_effect=lambda: next(env_iter)), \
         patch("envoy_diff.watcher.time.sleep"):
        watch(snapshot_dir=new_dir, interval=0, max_cycles=0)

    assert new_dir.is_dir()


def test_watch_no_cycles_does_not_call_on_change(tmp_path):
    events = []
    env_iter = iter([{"A": "1"}])

    with patch("envoy_diff.watcher.load_from_env", side_effect=lambda: next(env_iter)), \
         patch("envoy_diff.watcher.time.sleep"):
        watch(snapshot_dir=tmp_path, interval=0, max_cycles=0, on_change=events.append)

    assert events == []
