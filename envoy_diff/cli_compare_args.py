"""cli_compare_args.py – CLI subcommand for named environment comparison."""
from __future__ import annotations

import argparse
import json
import sys

from envoy_diff.comparator import compare
from envoy_diff.cli import _load
from envoy_diff.formatter import format_diff_as_string
from envoy_diff.cli_filter_args import add_filter_args, apply_filters


def add_compare_subcommand(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    """Register the 'compare' subcommand."""
    p = subparsers.add_parser(
        "compare",
        help="Compare two named environments with rich metadata output.",
    )
    p.add_argument("left", help="Left environment file or '-' for current env.")
    p.add_argument("right", help="Right environment file or '-' for current env.")
    p.add_argument("--left-label", default="left", help="Label for the left environment.")
    p.add_argument("--right-label", default="right", help="Label for the right environment.")
    p.add_argument("--description", default="", help="Optional description for this comparison.")
    p.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    p.add_argument("--no-color", action="store_true", help="Disable coloured output.")
    add_filter_args(p)
    p.set_defaults(func=run_compare_command)


def run_compare_command(args: argparse.Namespace) -> int:
    """Execute the compare subcommand; returns an exit code."""
    left_env = _load(args.left)
    right_env = _load(args.right)

    left_env = apply_filters(left_env, args)
    right_env = apply_filters(right_env, args)

    result = compare(
        left_env,
        right_env,
        left_label=args.left_label,
        right_label=args.right_label,
        description=args.description,
    )

    if args.output == "json":
        json.dump(result.as_dict(), sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        colour = not args.no_color
        text = format_diff_as_string(result.diff, colour=colour)
        label_line = (
            f"Comparing {result.context.left_label!r} "
            f"vs {result.context.right_label!r}"
        )
        if result.context.description:
            label_line += f" — {result.context.description}"
        sys.stdout.write(label_line + "\n")
        sys.stdout.write(text + "\n")
        score = result.score
        sys.stdout.write(
            f"Risk score: {score.total} ({score.risk_label})\n"
        )

    return 1 if result.summary.total_changes > 0 else 0
