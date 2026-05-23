"""Tests for envoy_diff.cli_compare_args."""
from __future__ import annotations

import argparse
import json
import os
import sys
from io import StringIO

import pytest

from envoy_diff.cli_compare_args import add_compare_subcommand, run_compare_command


def _make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command")
    add_compare_subcommand(sub)
    return p


def _write_json(path, data: dict) -> None:
    with open(path, "w") as fh:
        json.dump(data, fh)


def _ns(tmp_path, left: dict, right: dict, **kwargs) -> argparse.Namespace:
    lp = tmp_path / "left.json"
    rp = tmp_path / "right.json"
    _write_json(lp, left)
    _write_json(rp, right)
    defaults = dict(
        left=str(lp),
        right=str(rp),
        left_label="left",
        right_label="right",
        description="",
        output="text",
        no_color=True,
        prefix=None,
        include=[],
        exclude=[],
        regex=None,
        func=run_compare_command,
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_add_compare_subcommand_registers_compare():
    p = _make_parser()
    ns = p.parse_args(["compare", "a", "b"])
    assert ns.command == "compare"


def test_compare_defaults(tmp_path):
    p = _make_parser()
    lp = tmp_path / "l.json"
    rp = tmp_path / "r.json"
    _write_json(lp, {})
    _write_json(rp, {})
    ns = p.parse_args(["compare", str(lp), str(rp)])
    assert ns.left_label == "left"
    assert ns.right_label == "right"
    assert ns.output == "text"


def test_compare_returns_0_when_identical(tmp_path, capsys):
    ns = _ns(tmp_path, {"A": "1"}, {"A": "1"})
    code = run_compare_command(ns)
    assert code == 0


def test_compare_returns_1_when_different(tmp_path, capsys):
    ns = _ns(tmp_path, {"A": "1"}, {"A": "2"})
    code = run_compare_command(ns)
    assert code == 1


def test_compare_text_output_contains_label(tmp_path, capsys):
    ns = _ns(tmp_path, {}, {}, left_label="staging", right_label="prod")
    run_compare_command(ns)
    out = capsys.readouterr().out
    assert "staging" in out
    assert "prod" in out


def test_compare_text_output_contains_description(tmp_path, capsys):
    ns = _ns(tmp_path, {}, {}, description="weekly check")
    run_compare_command(ns)
    out = capsys.readouterr().out
    assert "weekly check" in out


def test_compare_json_output_is_valid_json(tmp_path, capsys):
    ns = _ns(tmp_path, {"X": "1"}, {"X": "2"}, output="json")
    run_compare_command(ns)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "context" in data
    assert "diff" in data


def test_compare_json_output_labels(tmp_path, capsys):
    ns = _ns(tmp_path, {}, {}, left_label="s", right_label="p", output="json")
    run_compare_command(ns)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["context"]["left_label"] == "s"
    assert data["context"]["right_label"] == "p"


def test_compare_text_output_ends_with_newline(tmp_path, capsys):
    ns = _ns(tmp_path, {}, {})
    run_compare_command(ns)
    out = capsys.readouterr().out
    assert out.endswith("\n")
