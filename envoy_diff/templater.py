"""Template rendering for env diff reports using simple string substitution."""

from __future__ import annotations

import re
from typing import Any

_PLACEHOLDER_RE = re.compile(r"\{\{\s*(\w+)\s*\}\}")


def render_template(template: str, context: dict[str, Any]) -> str:
    """Replace ``{{ key }}`` placeholders in *template* with values from *context*.

    Unknown placeholders are left unchanged.

    Args:
        template: A string containing ``{{ key }}`` placeholders.
        context: Mapping of placeholder names to replacement values.

    Returns:
        The rendered string.
    """
    if not isinstance(template, str):
        raise TypeError(f"template must be a str, got {type(template).__name__}")
    if not isinstance(context, dict):
        raise TypeError(f"context must be a dict, got {type(context).__name__}")

    def _replace(match: re.Match) -> str:  # type: ignore[type-arg]
        key = match.group(1)
        if key in context:
            return str(context[key])
        return match.group(0)  # leave unknown placeholders intact

    return _PLACEHOLDER_RE.sub(_replace, template)


def build_report_context(
    *,
    env_a_label: str = "a",
    env_b_label: str = "b",
    added: int = 0,
    removed: int = 0,
    changed: int = 0,
    unchanged: int = 0,
    score: float | None = None,
) -> dict[str, Any]:
    """Build a standard context dict for diff report templates."""
    total = added + removed + changed + unchanged
    ctx: dict[str, Any] = {
        "env_a": env_a_label,
        "env_b": env_b_label,
        "added": added,
        "removed": removed,
        "changed": changed,
        "unchanged": unchanged,
        "total": total,
    }
    if score is not None:
        ctx["score"] = round(score, 2)
    return ctx


DEFAULT_SUMMARY_TEMPLATE = (
    "Diff {{ env_a }} → {{ env_b }}: "
    "+{{ added }} -{{ removed }} ~{{ changed }} ({{ unchanged }} unchanged)"
)
