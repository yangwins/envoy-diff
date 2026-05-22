"""Command-line interface for envoy-diff."""

import argparse
import sys
from typing import Dict

from envoy_diff.loader import load_from_env, load_from_file
from envoy_diff.reporter import report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envoy-diff",
        description="Diff environment variable sets across deployments.",
    )
    parser.add_argument(
        "base",
        nargs="?",
        default=None,
        help="Base env file (JSON or .env). Omit to use current environment.",
    )
    parser.add_argument(
        "target",
        help="Target env file (JSON or .env) to compare against base.",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable coloured output.",
    )
    parser.add_argument(
        "--mask",
        action="store_true",
        default=False,
        help="Mask sensitive values (passwords, tokens, keys, etc.).",
    )
    parser.add_argument(
        "--show-length",
        action="store_true",
        default=False,
        help="When masking, append the original value length (e.g. ***(12)).",
    )
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    return parser


def _load(path: str) -> Dict[str, str]:
    """Load an env from a file path."""
    return load_from_file(path)


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    base_env = load_from_env() if args.base is None else _load(args.base)
    target_env = _load(args.target)

    return report(
        base_env,
        target_env,
        use_color=not args.no_color,
        output_format=args.output,
        mask=args.mask,
        show_length=args.show_length,
    )


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
