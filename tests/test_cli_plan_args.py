"""Tests for envoy_diff.cli_plan_args."""
from __future__ import annotations

import argparse
import json
import os
import tempfile
from io import StringIO

import pytest

from envoy_diff.cli_plan_args import add_plan_subcommand, run_plan_command


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command")
    add_plan_subcommand(sub)
    return parser


def _write_json(tmp_path, name: str, data: dict) -> str:
    p = os.path.join(tmp_path, name)
    with open(p, "w") as fh:
        json.dump(data, fh)
    return p


def _ns(base: str, head: str, fmt: str = "text", **kwargs) -> argparse.Namespace:
    ns = argparse.Namespace(
        base=base,
        head=head,
        plan_format=fmt,
        prefix=None,
        include=[],
        exclude=[],
        regex=None,
    )
    ns.__dict__.update(kwargs)
    return ns


# ---------------------------------------------------------------------------
# parser registration
# ---------------------------------------------------------------------------

def test_add_plan_subcommand_registers_plan():
    parser = _make_parser()
    args = parser.parse_args(["plan", "a.json", "b.json"])
    assert args.command == "plan"


def test_plan_defaults():
    parser = _make_parser()
    args = parser.parse_args(["plan", "a.json", "b.json"])
    assert args.plan_format == "text"


def test_plan_json_format_flag():
    parser = _make_parser()
    args = parser.parse_args(["plan", "a.json", "b.json", "--format", "json"])
    assert args.plan_format == "json"


# ---------------------------------------------------------------------------
# run_plan_command — exit codes
# ---------------------------------------------------------------------------

def test_run_plan_returns_0_when_identical(tmp_path):
    env = {"KEY": "value"}
    f = _write_json(tmp_path, "env.json", env)
    out = StringIO()
    code = run_plan_command(_ns(f, f), out)
    assert code == 0


def test_run_plan_returns_1_when_different(tmp_path):
    base = _write_json(tmp_path, "base.json", {"A": "1"})
    head = _write_json(tmp_path, "head.json", {"B": "2"})
    out = StringIO()
    code = run_plan_command(_ns(base, head), out)
    assert code == 1


# ---------------------------------------------------------------------------
# run_plan_command — text output
# ---------------------------------------------------------------------------

def test_run_plan_text_output_contains_key(tmp_path):
    base = _write_json(tmp_path, "base.json", {"OLD": "v"})
    head = _write_json(tmp_path, "head.json", {})
    out = StringIO()
    run_plan_command(_ns(base, head), out)
    assert "OLD" in out.getvalue()


def test_run_plan_text_output_ends_with_newline(tmp_path):
    base = _write_json(tmp_path, "base.json", {"X": "1"})
    head = _write_json(tmp_path, "head.json", {"X": "2"})
    out = StringIO()
    run_plan_command(_ns(base, head), out)
    assert out.getvalue().endswith("\n")


# ---------------------------------------------------------------------------
# run_plan_command — JSON output
# ---------------------------------------------------------------------------

def test_run_plan_json_output_is_valid_json(tmp_path):
    base = _write_json(tmp_path, "base.json", {"A": "1"})
    head = _write_json(tmp_path, "head.json", {"A": "2"})
    out = StringIO()
    run_plan_command(_ns(base, head, fmt="json"), out)
    data = json.loads(out.getvalue())
    assert "phases" in data


def test_run_plan_json_total_steps_correct(tmp_path):
    base = _write_json(tmp_path, "base.json", {"A": "1", "B": "2"})
    head = _write_json(tmp_path, "head.json", {"A": "changed", "C": "3"})
    out = StringIO()
    run_plan_command(_ns(base, head, fmt="json"), out)
    data = json.loads(out.getvalue())
    # A changed, B removed, C added => 3 steps
    assert data["total_steps"] == 3
