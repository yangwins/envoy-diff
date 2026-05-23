"""Watch environment variables for changes over time by polling snapshots."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

from envoy_diff.loader import load_from_env
from envoy_diff.differ import diff_envs, DiffResult, has_differences
from envoy_diff.snapshotter import save_snapshot, load_snapshot


@dataclass
class WatchEvent:
    """Emitted when a change is detected during a watch cycle."""

    cycle: int
    result: DiffResult
    previous_snapshot: Path
    timestamp: float = field(default_factory=time.time)

    @property
    def has_changes(self) -> bool:
        return has_differences(self.result)


def watch(
    snapshot_dir: Path,
    interval: float = 5.0,
    max_cycles: Optional[int] = None,
    on_change: Optional[Callable[[WatchEvent], None]] = None,
    on_cycle: Optional[Callable[[int], None]] = None,
) -> None:
    """Poll the live environment and emit events when it differs from the last snapshot.

    Args:
        snapshot_dir: Directory where snapshots are stored.
        interval: Seconds between polls.
        max_cycles: Stop after this many cycles (None = run forever).
        on_change: Callback invoked with a WatchEvent when changes are detected.
        on_cycle: Callback invoked with the cycle number on every iteration.
    """
    snapshot_dir = Path(snapshot_dir)
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    baseline_path = save_snapshot(load_from_env(), snapshot_dir)
    cycle = 0

    while max_cycles is None or cycle < max_cycles:
        time.sleep(interval)
        cycle += 1

        if on_cycle:
            on_cycle(cycle)

        current = load_from_env()
        previous = load_snapshot(baseline_path)
        result = diff_envs(previous, current)

        if has_differences(result):
            event = WatchEvent(cycle=cycle, result=result, previous_snapshot=baseline_path)
            if on_change:
                on_change(event)
            baseline_path = save_snapshot(current, snapshot_dir)
