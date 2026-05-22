"""Tests for envoy_diff.loader."""

import json
import os
import textwrap

import pytest

from envoy_diff.loader import (
    load_from_dict,
    load_from_env,
    load_from_file,
)


# ---------------------------------------------------------------------------
# load_from_env
# ---------------------------------------------------------------------------

def test_load_from_env_returns_current_environment(monkeypatch):
    monkeypatch.setenv("ENVOY_TEST_VAR", "hello")
    result = load_from_env()
    assert result["ENVOY_TEST_VAR"] == "hello"


def test_load_from_env_returns_dict():
    assert isinstance(load_from_env(), dict)


# ---------------------------------------------------------------------------
# load_from_dict
# ---------------------------------------------------------------------------

def test_load_from_dict_basic():
    result = load_from_dict({"KEY": "value", "PORT": 8080})
    assert result == {"KEY": "value", "PORT": "8080"}


def test_load_from_dict_coerces_to_str():
    result = load_from_dict({"NUM": 42, "FLAG": True})
    assert result["NUM"] == "42"
    assert result["FLAG"] == "True"


def test_load_from_dict_raises_on_non_dict():
    with pytest.raises(TypeError):
        load_from_dict(["KEY=value"])  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# load_from_file — JSON
# ---------------------------------------------------------------------------

def test_load_from_file_json(tmp_path):
    env_file = tmp_path / "env.json"
    env_file.write_text(json.dumps({"APP_ENV": "staging", "DEBUG": "true"}))
    result = load_from_file(env_file)
    assert result == {"APP_ENV": "staging", "DEBUG": "true"}


def test_load_from_file_json_invalid_root(tmp_path):
    env_file = tmp_path / "bad.json"
    env_file.write_text(json.dumps(["not", "a", "dict"]))
    with pytest.raises(ValueError, match="top-level object"):
        load_from_file(env_file)


# ---------------------------------------------------------------------------
# load_from_file — dotenv
# ---------------------------------------------------------------------------

def test_load_from_file_dotenv(tmp_path):
    content = textwrap.dedent("""\
        # comment
        APP_ENV=production
        SECRET_KEY="my secret"
        PORT='9000'
    """)
    env_file = tmp_path / ".env"
    env_file.write_text(content)
    result = load_from_file(env_file)
    assert result["APP_ENV"] == "production"
    assert result["SECRET_KEY"] == "my secret"
    assert result["PORT"] == "9000"


def test_load_from_file_dotenv_invalid_line(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("MISSING_EQUALS\n")
    with pytest.raises(ValueError, match="Invalid line"):
        load_from_file(env_file)


def test_load_from_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_from_file("/nonexistent/path/.env")
