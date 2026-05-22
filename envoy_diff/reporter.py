"""High-level reporter that ties together loading, diffing, and formatting."""

from __future__ import annotations

import sys
from typing import Optional, TextIO

from .differ import diff_envs, has_differences, DiffResult
from .formatter import format_diff_as_string
from .loader import load_from_file, load_from_env


def report(
    source_path: Optional[str],
    target_path: Optional[str],
    *,
    colour: bool = True,
    show_unchanged: bool = False,
    output: TextIO = sys.stdout,
) -> int:
    """Load two env sets, diff them, and write a formatted report.

    Parameters
    ----------
    source_path:
        Path to the *source* env file (JSON or .env).  When ``None`` the
        current process environment is used.
    target_path:
        Path to the *target* env file.  When ``None`` the current process
        environment is used.
    colour:
        Whether to emit ANSI colour codes in the output.
    show_unchanged:
        Include unchanged keys in the report.
    output:
        File-like object to write the report to.

    Returns
    -------
    int
        Exit code – ``0`` when the two env sets are identical, ``1`` when
        differences exist.
    """
    source_env = load_from_env() if source_path is None else load_from_file(source_path)
    target_env = load_from_env() if target_path is None else load_from_file(target_path)

    result: DiffResult = diff_envs(source_env, target_env)

    report_text = format_diff_as_string(
        result,
        colour=colour,
        show_unchanged=show_unchanged,
    )
    output.write(report_text)
    if not report_text.endswith("\n"):
        output.write("\n")

    return 1 if has_differences(result) else 0
