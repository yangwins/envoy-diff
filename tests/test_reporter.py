"""Tests for envoy_diff.reporter."""

from __future__ import annotations

import io
import json
import os
import tempfile
from pathlib import Path

import pytest

from envoy_diff.reporter import report


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_json(tmp_path: Path, data: dict) -> str:
    p = tmp_path / "env.json"
    p.write_text(json.dumps(data))
    return str(p)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_report_returns_0_when_identical(tmp_path):
    env = {"KEY": "value", "OTHER": "123"}
    src = _write_json(tmp_path / "a", env)
    (tmp_path / "a").mkdir(exist_ok=True)
    src = str(tmp_path / "a" / "env.json")
    Path(src).write_text(json.dumps(env))
    tgt = str(tmp_path / "b.json")
    Path(tgt).write_text(json.dumps(env))

    buf = io.StringIO()
    exit_code = report(src, tgt, colour=False, output=buf)

    assert exit_code == 0


def test_report_returns_1_when_different(tmp_path):
    src = str(tmp_path / "src.json")
    tgt = str(tmp_path / "tgt.json")
    Path(src).write_text(json.dumps({"A": "1"}))
    Path(tgt).write_text(json.dumps({"A": "2"}))

    buf = io.StringIO()
    exit_code = report(src, tgt, colour=False, output=buf)

    assert exit_code == 1


def test_report_output_contains_changed_key(tmp_path):
    src = str(tmp_path / "src.json")
    tgt = str(tmp_path / "tgt.json")
    Path(src).write_text(json.dumps({"MY_VAR": "old"}))
    Path(tgt).write_text(json.dumps({"MY_VAR": "new"}))

    buf = io.StringIO()
    report(src, tgt, colour=False, output=buf)

    assert "MY_VAR" in buf.getvalue()


def test_report_output_ends_with_newline(tmp_path):
    src = str(tmp_path / "src.json")
    tgt = str(tmp_path / "tgt.json")
    Path(src).write_text(json.dumps({"X": "1"}))
    Path(tgt).write_text(json.dumps({"X": "2"}))

    buf = io.StringIO()
    report(src, tgt, colour=False, output=buf)

    assert buf.getvalue().endswith("\n")


def test_report_added_key_appears_in_output(tmp_path):
    src = str(tmp_path / "src.json")
    tgt = str(tmp_path / "tgt.json")
    Path(src).write_text(json.dumps({}))
    Path(tgt).write_text(json.dumps({"NEW_KEY": "hello"}))

    buf = io.StringIO()
    report(src, tgt, colour=False, output=buf)

    assert "NEW_KEY" in buf.getvalue()


def test_report_removed_key_appears_in_output(tmp_path):
    src = str(tmp_path / "src.json")
    tgt = str(tmp_path / "tgt.json")
    Path(src).write_text(json.dumps({"GONE": "bye"}))
    Path(tgt).write_text(json.dumps({}))

    buf = io.StringIO()
    report(src, tgt, colour=False, output=buf)

    assert "GONE" in buf.getvalue()
