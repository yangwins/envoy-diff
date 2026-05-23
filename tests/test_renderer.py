"""Tests for envoy_diff.renderer."""
from __future__ import annotations

import pytest

from envoy_diff.differ import DiffResult
from envoy_diff.renderer import render_table


def _empty() -> DiffResult:
    return DiffResult(added={}, removed={}, changed={}, unchanged={})


def _make(*, added=None, removed=None, changed=None, unchanged=None) -> DiffResult:
    return DiffResult(
        added=added or {},
        removed=removed or {},
        changed=changed or {},
        unchanged=unchanged or {},
    )


# ---------------------------------------------------------------------------
# No differences
# ---------------------------------------------------------------------------

def test_render_empty_returns_no_differences_message():
    assert render_table(_empty()) == "(no differences)\n"


def test_render_only_unchanged_hidden_by_default():
    result = _make(unchanged={"FOO": "bar"})
    assert render_table(result) == "(no differences)\n"


# ---------------------------------------------------------------------------
# Output structure
# ---------------------------------------------------------------------------

def test_render_returns_string():
    result = _make(added={"NEW_KEY": "value"})
    assert isinstance(render_table(result), str)


def test_render_ends_with_newline():
    result = _make(added={"X": "1"})
    assert render_table(result).endswith("\n")


def test_render_header_present():
    result = _make(added={"A": "1"})
    output = render_table(result)
    assert "KEY" in output
    assert "STATUS" in output
    assert "LEFT" in output
    assert "RIGHT" in output


def test_render_separator_line_present():
    result = _make(added={"A": "1"})
    output = render_table(result)
    assert "-+-" in output


# ---------------------------------------------------------------------------
# Added / removed / changed
# ---------------------------------------------------------------------------

def test_render_shows_added_key():
    result = _make(added={"NEW": "hello"})
    output = render_table(result)
    assert "NEW" in output
    assert "added" in output
    assert "hello" in output


def test_render_shows_removed_key():
    result = _make(removed={"OLD": "bye"})
    output = render_table(result)
    assert "OLD" in output
    assert "removed" in output
    assert "bye" in output


def test_render_shows_changed_key():
    result = _make(changed={"VAR": ("old_val", "new_val")})
    output = render_table(result)
    assert "VAR" in output
    assert "changed" in output
    assert "old_val" in output
    assert "new_val" in output


# ---------------------------------------------------------------------------
# show_unchanged flag
# ---------------------------------------------------------------------------

def test_render_unchanged_hidden_by_default():
    result = _make(unchanged={"KEEP": "same"}, added={"X": "1"})
    output = render_table(result)
    assert "unchanged" not in output


def test_render_unchanged_shown_when_flag_set():
    result = _make(unchanged={"KEEP": "same"})
    output = render_table(result, show_unchanged=True)
    assert "KEEP" in output
    assert "unchanged" in output


# ---------------------------------------------------------------------------
# Sorting
# ---------------------------------------------------------------------------

def test_render_keys_are_sorted():
    result = _make(added={"ZEBRA": "z", "ALPHA": "a"})
    output = render_table(result)
    idx_alpha = output.index("ALPHA")
    idx_zebra = output.index("ZEBRA")
    assert idx_alpha < idx_zebra
