"""Tests for envoy_diff.cli_profile_args."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

from envoy_diff.cli_profile_args import add_profile_subcommands, run_profile_command
from envoy_diff.profiler import save_profile


def _make_parser():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command")
    add_profile_subcommands(sub)
    return parser


@pytest.fixture()
def profile_path(tmp_path: Path) -> Path:
    return tmp_path / "profiles.json"


def _ns(profile_path: Path, **kwargs) -> argparse.Namespace:
    base = {"profiles_file": str(profile_path)}
    base.update(kwargs)
    return argparse.Namespace(**base)


def test_add_profile_subcommands_registers_profile(tmp_path):
    parser = _make_parser()
    args = parser.parse_args(["profile", "list"])
    assert args.command == "profile"
    assert args.profile_cmd == "list"


def test_run_list_empty(profile_path, capsys):
    ns = _ns(profile_path, profile_cmd="list")
    rc = run_profile_command(ns)
    assert rc == 0
    assert "No profiles" in capsys.readouterr().out


def test_run_list_shows_names(profile_path, capsys):
    save_profile("staging", {"A": "1"}, profile_path)
    save_profile("prod", {"A": "2"}, profile_path)
    ns = _ns(profile_path, profile_cmd="list")
    run_profile_command(ns)
    out = capsys.readouterr().out
    assert "staging" in out
    assert "prod" in out


def test_run_save_from_file(profile_path, tmp_path, capsys):
    env_file = tmp_path / "env.json"
    env_file.write_text(json.dumps({"KEY": "val"}), encoding="utf-8")
    ns = _ns(profile_path, profile_cmd="save", name="test", file=str(env_file))
    rc = run_profile_command(ns)
    assert rc == 0
    assert "test" in capsys.readouterr().out


def test_run_show_existing_profile(profile_path, capsys):
    save_profile("staging", {"FOO": "bar"}, profile_path)
    ns = _ns(profile_path, profile_cmd="show", name="staging")
    rc = run_profile_command(ns)
    assert rc == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["FOO"] == "bar"


def test_run_show_missing_profile_returns_1(profile_path, capsys):
    ns = _ns(profile_path, profile_cmd="show", name="ghost")
    rc = run_profile_command(ns)
    assert rc == 1


def test_run_delete_existing_profile(profile_path, capsys):
    save_profile("staging", {"A": "1"}, profile_path)
    ns = _ns(profile_path, profile_cmd="delete", name="staging")
    rc = run_profile_command(ns)
    assert rc == 0


def test_run_delete_missing_profile_returns_1(profile_path, capsys):
    ns = _ns(profile_path, profile_cmd="delete", name="ghost")
    rc = run_profile_command(ns)
    assert rc == 1
