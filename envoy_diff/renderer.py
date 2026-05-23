"""Render diff results as structured plain-text tables."""
from __future__ import annotations

from typing import Sequence

from envoy_diff.differ import DiffResult

_HEADER = ("KEY", "STATUS", "LEFT", "RIGHT")
_STATUS_LABELS = {
    "added": "added",
    "removed": "removed",
    "changed": "changed",
    "unchanged": "unchanged",
}


def _col_widths(rows: Sequence[tuple[str, str, str, str]]) -> tuple[int, int, int, int]:
    """Return the maximum width for each of the four columns."""
    w0 = max(len(r[0]) for r in rows)
    w1 = max(len(r[1]) for r in rows)
    w2 = max(len(r[2]) for r in rows)
    w3 = max(len(r[3]) for r in rows)
    return w0, w1, w2, w3


def _build_rows(result: DiffResult) -> list[tuple[str, str, str, str]]:
    rows: list[tuple[str, str, str, str]] = [_HEADER]
    for key, val in sorted(result.added.items()):
        rows.append((key, "added", "", val))
    for key, val in sorted(result.removed.items()):
        rows.append((key, "removed", val, ""))
    for key, (left, right) in sorted(result.changed.items()):
        rows.append((key, "changed", left, right))
    for key, val in sorted(result.unchanged.items()):
        rows.append((key, "unchanged", val, val))
    return rows


def render_table(result: DiffResult, *, show_unchanged: bool = False) -> str:
    """Render *result* as a fixed-width plain-text table.

    Parameters
    ----------
    result:
        The :class:`~envoy_diff.differ.DiffResult` to render.
    show_unchanged:
        When *False* (default) unchanged keys are omitted from the output.

    Returns
    -------
    str
        A multi-line string table, terminated with a newline.
    """
    filtered = result
    if not show_unchanged:
        filtered = DiffResult(
            added=result.added,
            removed=result.removed,
            changed=result.changed,
            unchanged={},
        )

    rows = _build_rows(filtered)
    if len(rows) == 1:
        # Only the header — nothing to show.
        return "(no differences)\n"

    w0, w1, w2, w3 = _col_widths(rows)
    sep = "-+-".join("-" * w for w in (w0, w1, w2, w3))

    lines: list[str] = []
    for i, (c0, c1, c2, c3) in enumerate(rows):
        line = f"{c0:<{w0}} | {c1:<{w1}} | {c2:<{w2}} | {c3:<{w3}}"
        lines.append(line)
        if i == 0:
            lines.append(sep)
    lines.append("")
    return "\n".join(lines)
