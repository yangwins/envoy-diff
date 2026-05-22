"""Command-line interface for envoy-diff."""

import argparse
import sys
from typing import Optional, Sequence

from envoy_diff.loader import load_from_env, load_from_file
from envoy_diff.reporter import report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envoy-diff",
        description="Diff environment variable sets across deployments.",
    )
    parser.add_argument(
        "baseline",
        metavar="BASELINE",
        help="Path to baseline env file (.json or .env), or '-' to read from current environment.",
    )
    parser.add_argument(
        "target",
        metavar="TARGET",
        help="Path to target env file (.json or .env), or '-' to read from current environment.",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable coloured output.",
    )
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    return parser


def _load(path: str) -> dict:
    if path == "-":
        return load_from_env()
    return load_from_file(path)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        baseline = _load(args.baseline)
        target = _load(args.target)
    except (FileNotFoundError, ValueError) as exc:
        print(f"envoy-diff: error: {exc}", file=sys.stderr)
        return 2

    return report(
        baseline,
        target,
        use_color=not args.no_color,
        output_format=args.output,
    )


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
