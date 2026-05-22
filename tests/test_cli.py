"""Tests for the envoy_diff.cli module."""

import json
import os
from pathlib import Path

import pytest

from envoy_diff.cli import build_parser, main


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_json(tmp_path: Path, name: str, data: dict) -> str:
    p = tmp_path / name
    p.write_text(json.dumps(data))
    return str(p)


def _write_dotenv(tmp_path: Path, name: str, data: dict) -> str:
    p = tmp_path / name
    lines = [f"{k}={v}" for k, v in data.items()]
    p.write_text("\n".join(lines))
    return str(p)


# ---------------------------------------------------------------------------
# Parser tests
# ---------------------------------------------------------------------------

def test_build_parser_returns_parser():
    parser = build_parser()
    assert parser.prog == "envoy-diff"


def test_parser_defaults(tmp_path):
    baseline = _write_json(tmp_path, "a.json", {})
    target = _write_json(tmp_path, "b.json", {})
    parser = build_parser()
    args = parser.parse_args([baseline, target])
    assert args.no_color is False
    assert args.output == "text"


def test_parser_no_color_flag(tmp_path):
    baseline = _write_json(tmp_path, "a.json", {})
    target = _write_json(tmp_path, "b.json", {})
    parser = build_parser()
    args = parser.parse_args([baseline, target, "--no-color"])
    assert args.no_color is True


def test_parser_output_json(tmp_path):
    baseline = _write_json(tmp_path, "a.json", {})
    target = _write_json(tmp_path, "b.json", {})
    parser = build_parser()
    args = parser.parse_args([baseline, target, "--output", "json"])
    assert args.output == "json"


# ---------------------------------------------------------------------------
# main() integration tests
# ---------------------------------------------------------------------------

def test_main_returns_0_for_identical_files(tmp_path):
    data = {"KEY": "value"}
    baseline = _write_json(tmp_path, "a.json", data)
    target = _write_json(tmp_path, "b.json", data)
    assert main([baseline, target, "--no-color"]) == 0


def test_main_returns_1_for_different_files(tmp_path):
    baseline = _write_json(tmp_path, "a.json", {"KEY": "old"})
    target = _write_json(tmp_path, "b.json", {"KEY": "new"})
    assert main([baseline, target, "--no-color"]) == 1


def test_main_returns_2_for_missing_file(tmp_path):
    missing = str(tmp_path / "nonexistent.json")
    existing = _write_json(tmp_path, "b.json", {})
    assert main([missing, existing, "--no-color"]) == 2


def test_main_accepts_dotenv_files(tmp_path):
    baseline = _write_dotenv(tmp_path, "a.env", {"FOO": "bar"})
    target = _write_dotenv(tmp_path, "b.env", {"FOO": "bar"})
    assert main([baseline, target, "--no-color"]) == 0


def test_main_dash_reads_current_environment(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_TEST_KEY", "hello")
    target = _write_json(tmp_path, "target.json", {"ENVOY_TEST_KEY": "hello"})
    # Both sides should share at least ENVOY_TEST_KEY, result depends on full env
    result = main(["-", target, "--no-color"])
    assert result in (0, 1)


def test_main_json_output_is_valid_json(tmp_path, capsys):
    baseline = _write_json(tmp_path, "a.json", {"A": "1"})
    target = _write_json(tmp_path, "b.json", {"A": "2"})
    main([baseline, target, "--output", "json", "--no-color"])
    captured = capsys.readouterr()
    parsed = json.loads(captured.out)
    assert isinstance(parsed, dict)
