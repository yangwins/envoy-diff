"""Tests for envoy_diff.cli_watch_args."""

from __future__ import annotations

import argparse
from pathlib import Path
from unittest.mock import patch, call

import pytest

from envoy_diff.cli_watch_args import add_watch_subcommand, run_watch_command


def _make_parser() -> tuple[argparse.ArgumentParser, argparse._SubParsersAction]:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    add_watch_subcommand(subparsers)
    return parser, subparsers


def _ns(**kwargs) -> argparse.Namespace:
    defaults = {
        "interval": 5.0,
        "cycles": 2,
        "snapshot_dir": ".envoy_snapshots",
        "no_color": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


# ---------------------------------------------------------------------------
# Parser registration
# ---------------------------------------------------------------------------

def test_add_watch_subcommand_registers_watch():
    parser, _ = _make_parser()
    args = parser.parse_args(["watch"])
    assert hasattr(args, "func")


def test_watch_defaults():
    parser, _ = _make_parser()
    args = parser.parse_args(["watch"])
    assert args.interval == 5.0
    assert args.cycles is None
    assert args.snapshot_dir == ".envoy_snapshots"
    assert args.no_color is False


def test_watch_interval_flag():
    parser, _ = _make_parser()
    args = parser.parse_args(["watch", "--interval", "10"])
    assert args.interval == 10.0


def test_watch_cycles_flag():
    parser, _ = _make_parser()
    args = parser.parse_args(["watch", "--cycles", "3"])
    assert args.cycles == 3


def test_watch_no_color_flag():
    parser, _ = _make_parser()
    args = parser.parse_args(["watch", "--no-color"])
    assert args.no_color is True


# ---------------------------------------------------------------------------
# run_watch_command
# ---------------------------------------------------------------------------

def test_run_watch_command_returns_0(tmp_path, capsys):
    with patch("envoy_diff.cli_watch_args.watch") as mock_watch:
        mock_watch.return_value = None
        result = run_watch_command(_ns(snapshot_dir=str(tmp_path), cycles=0))
    assert result == 0


def test_run_watch_command_passes_interval(tmp_path):
    with patch("envoy_diff.cli_watch_args.watch") as mock_watch:
        run_watch_command(_ns(snapshot_dir=str(tmp_path), interval=2.5, cycles=1))
        _, kwargs = mock_watch.call_args
        assert kwargs["interval"] == 2.5


def test_run_watch_command_passes_max_cycles(tmp_path):
    with patch("envoy_diff.cli_watch_args.watch") as mock_watch:
        run_watch_command(_ns(snapshot_dir=str(tmp_path), cycles=7))
        _, kwargs = mock_watch.call_args
        assert kwargs["max_cycles"] == 7


def test_run_watch_command_handles_keyboard_interrupt(tmp_path, capsys):
    with patch("envoy_diff.cli_watch_args.watch", side_effect=KeyboardInterrupt):
        result = run_watch_command(_ns(snapshot_dir=str(tmp_path)))
    assert result == 0
    captured = capsys.readouterr()
    assert "stopped" in captured.out
