"""CLI argument helpers for the *transform* sub-command.

Allows users to apply key/value transformations before diffing:

    envoy-diff transform --strip-prefix APP_ --rename OLD:NEW \\
        --substitute '<unset>:' staging.json prod.json
"""

from __future__ import annotations

import argparse
from typing import Dict

from envoy_diff.transformer import transform_env
from envoy_diff.loader import load_from_file


def add_transform_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the *transform* sub-command onto *subparsers*."""
    p = subparsers.add_parser(
        "transform",
        help="Transform env keys/values then print the result as JSON.",
    )
    p.add_argument("file", help="JSON or .env file to transform.")
    p.add_argument(
        "--strip-prefix",
        metavar="PREFIX",
        default=None,
        help="Strip PREFIX from every key that starts with it.",
    )
    p.add_argument(
        "--rename",
        metavar="OLD:NEW",
        action="append",
        default=[],
        dest="renames",
        help="Rename a key. May be supplied multiple times.",
    )
    p.add_argument(
        "--substitute",
        metavar="OLD:NEW",
        action="append",
        default=[],
        dest="substitutions",
        help="Replace a value. May be supplied multiple times.",
    )
    p.set_defaults(func=run_transform_command)


def _parse_pairs(pairs: list[str]) -> Dict[str, str]:
    """Parse a list of ``'OLD:NEW'`` strings into a dict."""
    result: Dict[str, str] = {}
    for pair in pairs:
        if ":" not in pair:
            raise argparse.ArgumentTypeError(
                f"Expected OLD:NEW format, got: {pair!r}"
            )
        old, new = pair.split(":", 1)
        result[old] = new
    return result


def run_transform_command(args: argparse.Namespace) -> int:
    """Execute the transform sub-command; returns an exit code."""
    import json

    env = load_from_file(args.file)
    key_mapping = _parse_pairs(args.renames)
    value_subs = _parse_pairs(args.substitutions)

    transformed = transform_env(
        env,
        strip_prefix_str=args.strip_prefix,
        key_mapping=key_mapping or None,
        value_substitutions=value_subs or None,
    )

    print(json.dumps(transformed, indent=2, sort_keys=True))
    return 0
