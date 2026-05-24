"""Helpers to attach and read filter-related CLI arguments."""

import argparse
from typing import Dict, List, Optional

from envoy_diff.filter import filter_env, filter_keys_by_regex


def add_filter_args(parser: argparse.ArgumentParser) -> None:
    """Attach filter-related arguments to *parser* in-place."""
    grp = parser.add_argument_group("filtering")
    grp.add_argument(
        "--prefix",
        metavar="PREFIX",
        default=None,
        help="Only compare keys that start with PREFIX.",
    )
    grp.add_argument(
        "--include",
        metavar="PATTERN",
        nargs="+",
        default=None,
        help="Glob patterns; only matching keys are compared.",
    )
    grp.add_argument(
        "--exclude",
        metavar="PATTERN",
        nargs="+",
        default=None,
        help="Glob patterns; matching keys are excluded from comparison.",
    )
    grp.add_argument(
        "--regex",
        metavar="PATTERN",
        default=None,
        help="Regex; only keys matching this pattern are compared.",
    )


def apply_filters(
    env: Dict[str, str],
    prefix: Optional[str] = None,
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
    regex: Optional[str] = None,
) -> Dict[str, str]:
    """Apply all active filters to *env* and return the result."""
    result = filter_env(env, include=include, exclude=exclude, prefix=prefix)
    if regex:
        result = filter_keys_by_regex(result, regex)
    return result


def apply_filters_from_args(
    env: Dict[str, str],
    args: argparse.Namespace,
) -> Dict[str, str]:
    """Convenience wrapper that reads filter options directly from parsed *args*.

    Extracts ``prefix``, ``include``, ``exclude``, and ``regex`` attributes
    from *args* (as produced by :func:`add_filter_args`) and delegates to
    :func:`apply_filters`.
    """
    return apply_filters(
        env,
        prefix=getattr(args, "prefix", None),
        include=getattr(args, "include", None),
        exclude=getattr(args, "exclude", None),
        regex=getattr(args, "regex", None),
    )
