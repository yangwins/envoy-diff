"""cli_plan_args.py — CLI subcommand: envoy-diff plan.

Usage examples
--------------
  envoy-diff plan staging.json production.json
  envoy-diff plan staging.json production.json --format json
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import List

from envoy_diff.cli_filter_args import add_filter_args, apply_filters
from envoy_diff.differ import diff_envs
from envoy_diff.loader import load_from_file
from envoy_diff.planner import format_plan, plan_rollout


def add_plan_subcommand(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    """Register the *plan* subcommand onto *subparsers*."""
    parser: argparse.ArgumentParser = subparsers.add_parser(
        "plan",
        help="Generate a phased rollout plan from two env files.",
    )
    parser.add_argument("base", help="Base environment file (JSON or .env).")
    parser.add_argument("head", help="Head environment file (JSON or .env).")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="plan_format",
        help="Output format (default: text).",
    )
    add_filter_args(parser)


def run_plan_command(args: argparse.Namespace, out=sys.stdout) -> int:
    """Execute the *plan* subcommand; return an exit code."""
    base_env = load_from_file(args.base)
    head_env = load_from_file(args.head)

    base_env = apply_filters(base_env, args)
    head_env = apply_filters(head_env, args)

    result = diff_envs(base_env, head_env)
    plan = plan_rollout(result)

    if args.plan_format == "json":
        out.write(json.dumps(plan.as_dict(), indent=2))
        out.write("\n")
    else:
        out.write(format_plan(plan))

    # Exit 1 when there are steps, 0 when nothing to do.
    return 0 if plan.is_empty() else 1
