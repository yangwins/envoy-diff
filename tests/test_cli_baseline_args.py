"""Tests for envoy_diff.cli_baseline_args."""

from __future__ import annotations

import argparse
import json
from io import StringIO
from pathlib import Path

import pytest

from envoy_diff.cli_baseline_args import add_baseline_subcommands, run_baseline_command
from envoy_diff.baseline import save_baseline


def _make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command")
    add_baseline_subcommands(sub)
    return p


def _ns(parser, args):
    return parser.parse_args(args)


ENV = {"KEY": "value", "OTHER": "123"}


def test_add_baseline_subcommands_registers_baseline():
    p = _make_parser()
    ns = _ns(p, ["baseline", "save"])
    assert ns.command == "baseline"
    assert ns.baseline_cmd == "save"


def test_save_defaults(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    p = _make_parser()
    ns = _ns(p, ["baseline", "save"])
    assert ns.file is None
    assert ns.output is None
    assert ns.overwrite is False


def test_save_creates_baseline(tmp_path, monkeypatch):
    bl = tmp_path / ".envoy_baseline.json"
    monkeypatch.setenv("SOME_KEY", "hello")
    p = _make_parser()
    ns = _ns(p, ["baseline", "save", "--output", str(bl)])
    out, err = StringIO(), StringIO()
    rc = run_baseline_command(ns, out=out, err=err)
    assert rc == 0
    assert bl.exists()
    assert "Baseline saved" in out.getvalue()


def test_save_errors_on_existing_without_overwrite(tmp_path):
    bl = tmp_path / ".envoy_baseline.json"
    save_baseline(ENV, path=bl)
    p = _make_parser()
    ns = _ns(p, ["baseline", "save", "--output", str(bl)])
    out, err = StringIO(), StringIO()
    rc = run_baseline_command(ns, out=out, err=err)
    assert rc == 1
    assert "Error" in err.getvalue()


def test_save_overwrite_flag(tmp_path):
    bl = tmp_path / ".envoy_baseline.json"
    save_baseline(ENV, path=bl)
    p = _make_parser()
    ns = _ns(p, ["baseline", "save", "--output", str(bl), "--overwrite"])
    out, err = StringIO(), StringIO()
    rc = run_baseline_command(ns, out=out, err=err)
    assert rc == 0


def test_info_shows_metadata(tmp_path):
    bl = tmp_path / ".envoy_baseline.json"
    save_baseline(ENV, path=bl)
    p = _make_parser()
    ns = _ns(p, ["baseline", "info", "--path", str(bl)])
    out, err = StringIO(), StringIO()
    rc = run_baseline_command(ns, out=out, err=err)
    assert rc == 0
    assert "saved_at" in out.getvalue()
    assert "key_count" in out.getvalue()


def test_info_missing_baseline_returns_1(tmp_path):
    bl = tmp_path / ".envoy_baseline.json"
    p = _make_parser()
    ns = _ns(p, ["baseline", "info", "--path", str(bl)])
    out, err = StringIO(), StringIO()
    rc = run_baseline_command(ns, out=out, err=err)
    assert rc == 1


def test_clear_removes_baseline(tmp_path):
    bl = tmp_path / ".envoy_baseline.json"
    save_baseline(ENV, path=bl)
    p = _make_parser()
    ns = _ns(p, ["baseline", "clear", "--path", str(bl)])
    out, err = StringIO(), StringIO()
    rc = run_baseline_command(ns, out=out, err=err)
    assert rc == 0
    assert not bl.exists()


def test_clear_missing_returns_1(tmp_path):
    bl = tmp_path / ".envoy_baseline.json"
    p = _make_parser()
    ns = _ns(p, ["baseline", "clear", "--path", str(bl)])
    out, err = StringIO(), StringIO()
    rc = run_baseline_command(ns, out=out, err=err)
    assert rc == 1
