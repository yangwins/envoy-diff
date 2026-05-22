"""Export diff results to various output formats (JSON, CSV, Markdown)."""

from __future__ import annotations

import csv
import io
import json
from typing import Literal

from envoy_diff.differ import DiffResult

OutputFormat = Literal["json", "csv", "markdown"]


def export_diff(result: DiffResult, fmt: OutputFormat) -> str:
    """Export a DiffResult to the requested format string.

    Args:
        result: The diff result produced by ``diff_envs``.
        fmt:    One of ``'json'``, ``'csv'``, or ``'markdown'``.

    Returns:
        A string representation of the diff in the chosen format.

    Raises:
        ValueError: If *fmt* is not a recognised format.
    """
    if fmt == "json":
        return _export_json(result)
    if fmt == "csv":
        return _export_csv(result)
    if fmt == "markdown":
        return _export_markdown(result)
    raise ValueError(f"Unknown export format: {fmt!r}. Choose from 'json', 'csv', 'markdown'.")


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _rows(result: DiffResult) -> list[dict[str, str]]:
    """Flatten a DiffResult into a list of row dicts suitable for tabular export."""
    rows: list[dict[str, str]] = []

    for key, (old_val, new_val) in result.changed.items():
        rows.append({"status": "changed", "key": key, "old_value": old_val, "new_value": new_val})

    for key, value in result.added.items():
        rows.append({"status": "added", "key": key, "old_value": "", "new_value": value})

    for key, value in result.removed.items():
        rows.append({"status": "removed", "key": key, "old_value": value, "new_value": ""})

    for key, value in result.unchanged.items():
        rows.append({"status": "unchanged", "key": key, "old_value": value, "new_value": value})

    # Stable output — sort by status priority then key name
    _priority = {"changed": 0, "added": 1, "removed": 2, "unchanged": 3}
    rows.sort(key=lambda r: (_priority[r["status"]], r["key"]))
    return rows


def _export_json(result: DiffResult) -> str:
    """Serialise the diff as a JSON object with one array per status bucket."""
    payload = {
        "changed": [
            {"key": k, "old_value": old, "new_value": new}
            for k, (old, new) in sorted(result.changed.items())
        ],
        "added": [
            {"key": k, "value": v}
            for k, v in sorted(result.added.items())
        ],
        "removed": [
            {"key": k, "value": v}
            for k, v in sorted(result.removed.items())
        ],
        "unchanged": [
            {"key": k, "value": v}
            for k, v in sorted(result.unchanged.items())
        ],
    }
    return json.dumps(payload, indent=2)


def _export_csv(result: DiffResult) -> str:
    """Serialise the diff as CSV with columns: status, key, old_value, new_value."""
    buf = io.StringIO()
    fieldnames = ["status", "key", "old_value", "new_value"]
    writer = csv.DictWriter(buf, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(_rows(result))
    return buf.getvalue()


def _export_markdown(result: DiffResult) -> str:
    """Serialise the diff as a GitHub-flavoured Markdown table."""
    rows = _rows(result)
    lines: list[str] = [
        "| Status | Key | Old Value | New Value |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        status = row["status"]
        key = _md_escape(row["key"])
        old = _md_escape(row["old_value"]) or "—"
        new = _md_escape(row["new_value"]) or "—"
        lines.append(f"| {status} | {key} | {old} | {new} |")
    return "\n".join(lines) + "\n"


def _md_escape(text: str) -> str:
    """Escape pipe characters so they don't break Markdown table cells."""
    return text.replace("|", "\\|")
