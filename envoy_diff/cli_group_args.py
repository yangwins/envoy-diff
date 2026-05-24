"""CLI sub-command: envoy-diff group — group diff keys by prefix or mapping."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List

from envoy_diff.cli import _load
from envoy_diff.differ import diff_envs
from envoy_diff.grouper import GroupedDiff, group_by_mapping, group_by_prefix


def add_group_subcommand(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    """Register the *group* sub-command on *subparsers*."""
    p: argparse.ArgumentParser = subparsers.add_parser(
        "group",
        help="Group diff keys by prefix or an explicit key→group mapping.",
    )
    p.add_argument("env_a", help="Path to first env file (JSON or .env).")
    p.add_argument("env_b", help="Path to second env file (JSON or .env).")

    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--prefix",
        metavar="PREFIX",
        nargs="+",
        dest="prefixes",
        help="One or more key prefixes to group by (e.g. APP DB REDIS).",
    )
    mode.add_argument(
        "--mapping",
        metavar="GROUP:KEY",
        nargs="+",
        dest="mapping_pairs",
        help="Explicit group assignments in GROUP:KEY format.",
    )

    p.add_argument(
        "--include-unchanged",
        action="store_true",
        default=False,
        help="Also group unchanged keys (hidden by default).",
    )
    p.add_argument(
        "--separator",
        default="_",
        help="Separator between prefix and key name (default: '_').",
    )
    p.set_defaults(func=run_group_command)


def _parse_mapping_pairs(pairs: List[str]) -> dict:
    """Convert ['GROUP:KEY', ...] into {group: [key, ...]} dict."""
    mapping: dict = {}
    for pair in pairs:
        if ":" not in pair:
            raise argparse.ArgumentTypeError(
                f"Invalid mapping pair {pair!r}. Expected GROUP:KEY."
            )
        group, key = pair.split(":", 1)
        mapping.setdefault(group, []).append(key)
    return mapping


def run_group_command(args: argparse.Namespace) -> int:
    """Execute the *group* sub-command and print JSON to stdout."""
    try:
        env_a = _load(args.env_a)
        env_b = _load(args.env_b)
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    result = diff_envs(env_a, env_b)

    if args.prefixes:
        gd: GroupedDiff = group_by_prefix(
            result,
            args.prefixes,
            separator=args.separator,
            include_unchanged=args.include_unchanged,
        )
    else:
        try:
            mapping = _parse_mapping_pairs(args.mapping_pairs)
        except argparse.ArgumentTypeError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        gd = group_by_mapping(
            result,
            mapping,
            include_unchanged=args.include_unchanged,
        )

    print(json.dumps(gd.as_dict(), indent=2))
    return 0
