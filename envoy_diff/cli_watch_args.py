"""CLI sub-command: envoy-diff watch — poll live env and report changes."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envoy_diff.watcher import WatchEvent, watch
from envoy_diff.formatter import format_diff_as_string
from envoy_diff.summarizer import format_summary, summarize


def add_watch_subcommand(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    """Register the *watch* sub-command on *subparsers*."""
    p = subparsers.add_parser(
        "watch",
        help="Poll the live environment and report when it changes.",
    )
    p.add_argument(
        "--interval",
        type=float,
        default=5.0,
        metavar="SECONDS",
        help="Seconds between polls (default: 5).",
    )
    p.add_argument(
        "--cycles",
        type=int,
        default=None,
        metavar="N",
        help="Stop after N cycles (default: run forever).",
    )
    p.add_argument(
        "--snapshot-dir",
        default=".envoy_snapshots",
        metavar="DIR",
        help="Directory to store baseline snapshots (default: .envoy_snapshots).",
    )
    p.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable coloured output.",
    )
    p.set_defaults(func=run_watch_command)


def run_watch_command(args: argparse.Namespace) -> int:
    """Entry point for the *watch* sub-command."""
    color = not args.no_color
    snapshot_dir = Path(args.snapshot_dir)

    print(f"[envoy-diff watch] polling every {args.interval}s — Ctrl-C to stop",
          flush=True)

    def on_change(event: WatchEvent) -> None:
        summary = format_summary(summarize(event.result))
        diff_str = format_diff_as_string(event.result, color=color)
        print(f"\n[cycle {event.cycle}] change detected — {summary}")
        print(diff_str, flush=True)

    def on_cycle(cycle: int) -> None:
        print(f"[cycle {cycle}] no changes", flush=True)

    try:
        watch(
            snapshot_dir=snapshot_dir,
            interval=args.interval,
            max_cycles=args.cycles,
            on_change=on_change,
            on_cycle=on_cycle,
        )
    except KeyboardInterrupt:
        print("\n[envoy-diff watch] stopped.", flush=True)

    return 0
