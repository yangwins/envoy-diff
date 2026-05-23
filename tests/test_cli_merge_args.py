"""Tests for envoy_diff.cli_merge_args."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

from envoy_diff.cli_merge_args import add_merge_subcommand, run_merge_command


def _make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    add_merge_subcommand(subparsers)
    return parser


def _write_json(path: Path, data: dict) -> Path:
    path.write_text(json.dumps(data))
    return path


def _ns(tmp_path: Path, base: dict, override: dict, **kwargs):
    base_file = _write_json(tmp_path / "base.json", base)
    override_file = _write_json(tmp_path / "override.json", override)
    defaults = dict(
        base=str(base_file),
        override=str(override_file),
        strategy="right",
        prefix=None,
        diff=False,
        no_color=True,
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_add_merge_subcommand_registers_merge():
    parser = _make_parser()
    parsed = parser.parse_args(["merge", "a.json", "b.json"])
    assert parsed.func is run_merge_command


def test_merge_defaults(tmp_path):
    parser = _make_parser()
    base = _write_json(tmp_path / "b.json", {})
    override = _write_json(tmp_path / "o.json", {})
    parsed = parser.parse_args(["merge", str(base), str(override)])
    assert parsed.strategy == "right"
    assert parsed.prefix is None
    assert parsed.diff is False
    assert parsed.no_color is False


def test_merge_strategy_flag(tmp_path):
    parser = _make_parser()
    base = _write_json(tmp_path / "b.json", {})
    override = _write_json(tmp_path / "o.json", {})
    parsed = parser.parse_args(["merge", str(base), str(override), "--strategy", "left"])
    assert parsed.strategy == "left"


def test_run_merge_command_returns_0_on_success(tmp_path, capsys):
    ns = _ns(tmp_path, {"A": "1"}, {"B": "2"})
    rc = run_merge_command(ns)
    assert rc == 0


def test_run_merge_command_outputs_merged_keys(tmp_path, capsys):
    ns = _ns(tmp_path, {"A": "1"}, {"B": "2"})
    run_merge_command(ns)
    out = capsys.readouterr().out
    assert "A=1" in out
    assert "B=2" in out


def test_run_merge_command_right_wins(tmp_path, capsys):
    ns = _ns(tmp_path, {"KEY": "old"}, {"KEY": "new"}, strategy="right")
    run_merge_command(ns)
    out = capsys.readouterr().out
    assert "KEY=new" in out


def test_run_merge_command_left_wins(tmp_path, capsys):
    ns = _ns(tmp_path, {"KEY": "original"}, {"KEY": "ignored"}, strategy="left")
    run_merge_command(ns)
    out = capsys.readouterr().out
    assert "KEY=original" in out


def test_run_merge_command_strict_conflict_returns_2(tmp_path):
    ns = _ns(tmp_path, {"KEY": "val1"}, {"KEY": "val2"}, strategy="strict")
    rc = run_merge_command(ns)
    assert rc == 2


def test_run_merge_command_diff_flag_returns_int(tmp_path):
    ns = _ns(tmp_path, {"A": "1"}, {"A": "2"}, diff=True)
    rc = run_merge_command(ns)
    assert isinstance(rc, int)


def test_run_merge_command_prefix_filters_keys(tmp_path, capsys):
    ns = _ns(
        tmp_path,
        {"APP_HOST": "localhost"},
        {"APP_PORT": "8080", "DB_HOST": "db"},
        prefix="APP_",
    )
    run_merge_command(ns)
    out = capsys.readouterr().out
    assert "APP_PORT" in out
    assert "DB_HOST" not in out
