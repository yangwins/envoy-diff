"""CLI helpers for snapshot sub-commands (save / load)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

from envoy_diff.loader import load_from_env, load_from_file
from envoy_diff.snapshotter import load_snapshot, save_snapshot, snapshot_metadata


def add_snapshot_subcommands(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    """Register *snapshot-save* and *snapshot-info* sub-commands."""
    # --- snapshot-save -------------------------------------------------------
    save_p = subparsers.add_parser(
        "snapshot-save",
        help="Capture the current environment (or a file) as a snapshot.",
    )
    save_p.add_argument(
        "output",
        metavar="OUTPUT",
        help="Destination .json file for the snapshot.",
    )
    save_p.add_argument(
        "--from-file",
        metavar="FILE",
        dest="from_file",
        default=None,
        help="Load env from a .json or .env file instead of the live environment.",
    )
    save_p.add_argument(
        "--label",
        default="",
        help="Optional human-readable label stored in snapshot metadata.",
    )
    save_p.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="Overwrite an existing snapshot file.",
    )

    # --- snapshot-info -------------------------------------------------------
    info_p = subparsers.add_parser(
        "snapshot-info",
        help="Display metadata from a saved snapshot.",
    )
    info_p.add_argument(
        "snapshot",
        metavar="SNAPSHOT",
        help="Path to the .json snapshot file.",
    )


def run_snapshot_save(args: argparse.Namespace) -> int:
    """Execute the *snapshot-save* sub-command. Returns exit code."""
    env = load_from_file(args.from_file) if args.from_file else load_from_env()
    try:
        dest = save_snapshot(
            env,
            args.output,
            label=args.label or None,
            overwrite=args.overwrite,
        )
        print(f"Snapshot saved: {dest}  ({len(env)} keys)")
        return 0
    except FileExistsError as exc:
        print(f"error: {exc}  (use --overwrite to replace)", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


def run_snapshot_info(args: argparse.Namespace) -> int:
    """Execute the *snapshot-info* sub-command. Returns exit code."""
    try:
        meta = snapshot_metadata(args.snapshot)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(f"label      : {meta.get('label') or '(none)'}")
    print(f"created_at : {meta.get('created_at', 'unknown')}")
    print(f"key_count  : {meta.get('key_count', 'unknown')}")
    return 0
