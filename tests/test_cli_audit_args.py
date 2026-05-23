"""Tests for envoy_diff.cli_audit_args."""
import argparse
import json
from pathlib import Path

import pytest

from envoy_diff.auditor import record
from envoy_diff.cli_audit_args import add_audit_subcommands, run_audit_command


def _make_parser():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command")
    add_audit_subcommands(sub)
    return parser


def _ns(parser, args):
    return parser.parse_args(args)


def test_add_audit_subcommands_registers_audit():
    parser = _make_parser()
    ns = _ns(parser, ["audit", "list"])
    assert ns.command == "audit"


def test_audit_list_default_directory():
    parser = _make_parser()
    ns = _ns(parser, ["audit", "list"])
    assert ns.directory == "."


def test_audit_list_custom_directory():
    parser = _make_parser()
    ns = _ns(parser, ["audit", "list", "--directory", "/tmp"])
    assert ns.directory == "/tmp"


def test_audit_list_json_flag():
    parser = _make_parser()
    ns = _ns(parser, ["audit", "list", "--json"])
    assert ns.as_json is True


def test_audit_list_no_entries(tmp_path, capsys):
    parser = _make_parser()
    ns = _ns(parser, ["audit", "list", "--directory", str(tmp_path)])
    code = run_audit_command(ns)
    assert code == 0
    out = capsys.readouterr().out
    assert "No audit entries" in out


def test_audit_list_shows_entries(tmp_path, capsys):
    record("diff", "staging", "prod", 1, 0, 2, directory=tmp_path)
    parser = _make_parser()
    ns = _ns(parser, ["audit", "list", "--directory", str(tmp_path)])
    run_audit_command(ns)
    out = capsys.readouterr().out
    assert "staging" in out
    assert "prod" in out


def test_audit_list_json_output(tmp_path, capsys):
    record("diff", "a", "b", 1, 1, 1, directory=tmp_path)
    parser = _make_parser()
    ns = _ns(parser, ["audit", "list", "--json", "--directory", str(tmp_path)])
    run_audit_command(ns)
    out = capsys.readouterr().out
    parsed = json.loads(out)
    assert isinstance(parsed, list)
    assert len(parsed) == 1


def test_audit_clear_removes_log(tmp_path, capsys):
    record("diff", "a", "b", 0, 0, 0, directory=tmp_path)
    parser = _make_parser()
    ns = _ns(parser, ["audit", "clear", "--directory", str(tmp_path)])
    code = run_audit_command(ns)
    assert code == 0
    assert not (tmp_path / ".envoy_audit.json").exists()


def test_audit_no_subcommand_returns_1(tmp_path):
    parser = _make_parser()
    ns = _ns(parser, ["audit"])
    ns.directory = str(tmp_path)
    ns.audit_command = None
    code = run_audit_command(ns)
    assert code == 1
