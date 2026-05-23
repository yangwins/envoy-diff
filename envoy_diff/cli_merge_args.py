"""CLI sub-command: ``envoy-diff merge`` — merge two env files."""

from __future__ import annotations

import argparse
import sys
from typing import List

from envoy_diff.cli import _load
from envoy_diff.merger import MergeConflictError, MergeStrategy, merge_envs
from envoy_diff.reporter import report


def add_merge_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the *merge* sub-command onto *subparsers*."""
    parser: argparse.ArgumentParser = subparsers.add_parser(
        "merge",
        help="Merge two environment files and optionally diff the result.",
    )
    parser.add_argument("base", help="Base environment file (JSON or .env).")
    parser.add_argument("override", help="Override environment file (JSON or .env).")
    parser.add_argument(
        "--strategy",
        choices=[s.value for s in MergeStrategy],
        default=MergeStrategy.RIGHT.value,
        help="Conflict resolution strategy (default: right).",
    )
    parser.add_argument(
        "--prefix",
        default=None,
        metavar="PREFIX",
        help="Only merge keys from override that start with PREFIX.",
    )
    parser.add_argument(
        "--diff",
        action="store_true",
        default=False,
        help="After merging, diff base against the merged result and report.",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable ANSI colour output.",
    )
    parser.set_defaults(func=run_merge_command)


def run_merge_command(args: argparse.Namespace, argv: List[str] | None = None) -> int:
    """Execute the merge sub-command. Returns an exit code."""
    base_env = _load(args.base)
    override_env = _load(args.override)
    strategy = MergeStrategy(args.strategy)

    try:
        merged = merge_envs(
            base_env,
            override_env,
            strategy=strategy,
            prefix=args.prefix or None,
        )
    except MergeConflictError as exc:
        print(f"error: merge conflict — {exc}", file=sys.stderr)
        return 2

    if args.diff:
        return report(
            base_env,
            merged,
            use_color=not args.no_color,
            label_a=args.base,
            label_b="merged",
        )

    for key, value in sorted(merged.items()):
        print(f"{key}={value}")
    return 0
