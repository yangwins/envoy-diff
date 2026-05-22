"""Formatting utilities to render DiffResult as human-readable text."""

from typing import IO
import sys

from envoy_diff.differ import DiffResult

# ANSI colour codes
_GREEN = "\033[32m"
_RED = "\033[31m"
_YELLOW = "\033[33m"
_RESET = "\033[0m"


def _colour(text: str, code: str, use_colour: bool) -> str:
    if use_colour:
        return f"{code}{text}{_RESET}"
    return text


def format_diff(
    result: DiffResult,
    use_colour: bool = True,
    show_unchanged: bool = False,
    out: IO = None,
) -> None:
    """Print a DiffResult to *out* (defaults to stdout).

    Args:
        result: The DiffResult to render.
        use_colour: Whether to emit ANSI colour codes.
        show_unchanged: If True, also print unchanged keys.
        out: Output stream; defaults to sys.stdout.
    """
    if out is None:
        out = sys.stdout

    if not result.has_differences and not show_unchanged:
        print("No differences found.", file=out)
        return

    for key, value in sorted(result.added.items()):
        line = f"+ {key}={value}"
        print(_colour(line, _GREEN, use_colour), file=out)

    for key, value in sorted(result.removed.items()):
        line = f"- {key}={value}"
        print(_colour(line, _RED, use_colour), file=out)

    for key, (old_val, new_val) in sorted(result.changed.items()):
        line = f"~ {key}: {old_val!r} -> {new_val!r}"
        print(_colour(line, _YELLOW, use_colour), file=out)

    if show_unchanged:
        for key, value in sorted(result.unchanged.items()):
            print(f"  {key}={value}", file=out)

    print(file=out)
    print(result.summary, file=out)


def format_diff_as_string(
    result: DiffResult,
    use_colour: bool = False,
    show_unchanged: bool = False,
) -> str:
    """Return the formatted diff as a string instead of printing it."""
    import io

    buf = io.StringIO()
    format_diff(result, use_colour=use_colour, show_unchanged=show_unchanged, out=buf)
    return buf.getvalue()
