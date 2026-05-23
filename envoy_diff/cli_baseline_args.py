"""CLI sub-commands for baseline management: save, load-info, clear."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

from envoy_diff.baseline import (
    save_baseline,
    load_baseline,
    baseline_exists,
    clear_baseline,
    baseline_path,
)
from envoy_diff.loader import load_from_file, load_from_env
from envoy_diff.snapshotter import snapshot_metadata


def add_baseline_subcommands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register *baseline* sub-commands onto *subparsers*."""
    bl = subparsers.add_parser("baseline", help="Manage environment baselines")
    bl_sub = bl.add_subparsers(dest="baseline_cmd", required=True)

    # baseline save
    save_p = bl_sub.add_parser("save", help="Pin current env as the baseline")
    save_p.add_argument("--file", metavar="FILE", help="Load env from file instead of process env")
    save_p.add_argument("--output", metavar="PATH", help="Where to write the baseline (default: .envoy_baseline.json)")
    save_p.add_argument("--overwrite", action="store_true", help="Replace an existing baseline")

    # baseline info
    info_p = bl_sub.add_parser("info", help="Show baseline metadata")
    info_p.add_argument("--path", metavar="PATH", help="Path to baseline file")

    # baseline clear
    clear_p = bl_sub.add_parser("clear", help="Delete the baseline file")
    clear_p.add_argument("--path", metavar="PATH", help="Path to baseline file")


def run_baseline_command(ns: argparse.Namespace, out=sys.stdout, err=sys.stderr) -> int:
    """Dispatch to the appropriate baseline sub-command handler."""
    cmd = ns.baseline_cmd

    if cmd == "save":
        env = load_from_file(ns.file) if ns.file else load_from_env()
        dest = Path(ns.output) if ns.output else None
        try:
            path = save_baseline(env, path=dest, overwrite=ns.overwrite)
            out.write(f"Baseline saved to {path}\n")
            return 0
        except FileExistsError as exc:
            err.write(f"Error: {exc}\n")
            return 1

    if cmd == "info":
        src = Path(ns.path) if ns.path else None
        if not baseline_exists(path=src):
            err.write(f"No baseline found at {src or baseline_path()}\n")
            return 1
        effective = src if src else baseline_path()
        meta = snapshot_metadata(effective)
        out.write(f"path:      {effective}\n")
        out.write(f"saved_at:  {meta.get('saved_at', 'unknown')}\n")
        out.write(f"key_count: {meta.get('key_count', '?')}\n")
        return 0

    if cmd == "clear":
        src = Path(ns.path) if ns.path else None
        removed = clear_baseline(path=src)
        if removed:
            out.write("Baseline cleared.\n")
            return 0
        err.write("No baseline file found to clear.\n")
        return 1

    err.write(f"Unknown baseline command: {cmd}\n")
    return 1
