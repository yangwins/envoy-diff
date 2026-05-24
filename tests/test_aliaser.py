"""Tests for envoy_diff.aliaser."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envoy_diff.aliaser import (
    _aliases_path,
    apply_aliases,
    list_aliases,
    load_aliases,
    remove_alias,
    save_alias,
)


@pytest.fixture()
def alias_dir(tmp_path: Path) -> str:
    return str(tmp_path)


# ---------------------------------------------------------------------------
# _aliases_path
# ---------------------------------------------------------------------------

def test_aliases_path_default_is_cwd():
    p = _aliases_path()
    assert p.name == ".envoy_aliases.json"
    assert p.parent == Path.cwd()


def test_aliases_path_custom_directory(alias_dir):
    p = _aliases_path(alias_dir)
    assert p.parent == Path(alias_dir)


# ---------------------------------------------------------------------------
# load_aliases / save_alias
# ---------------------------------------------------------------------------

def test_load_aliases_empty_when_no_file(alias_dir):
    assert load_aliases(alias_dir) == {}


def test_save_alias_creates_file(alias_dir):
    save_alias("DB_HOST", "DATABASE_HOST", alias_dir)
    p = Path(alias_dir) / ".envoy_aliases.json"
    assert p.exists()


def test_save_alias_stores_mapping(alias_dir):
    save_alias("DB_HOST", "DATABASE_HOST", alias_dir)
    aliases = load_aliases(alias_dir)
    assert aliases["DB_HOST"] == "DATABASE_HOST"


def test_save_alias_multiple_keys(alias_dir):
    save_alias("A", "B", alias_dir)
    save_alias("C", "D", alias_dir)
    aliases = load_aliases(alias_dir)
    assert aliases == {"A": "B", "C": "D"}


def test_save_alias_returns_path(alias_dir):
    p = save_alias("X", "Y", alias_dir)
    assert isinstance(p, Path)
    assert p.exists()


# ---------------------------------------------------------------------------
# remove_alias
# ---------------------------------------------------------------------------

def test_remove_alias_returns_true_when_found(alias_dir):
    save_alias("KEY", "OTHER", alias_dir)
    assert remove_alias("KEY", alias_dir) is True


def test_remove_alias_returns_false_when_not_found(alias_dir):
    assert remove_alias("MISSING", alias_dir) is False


def test_remove_alias_deletes_key(alias_dir):
    save_alias("A", "B", alias_dir)
    save_alias("C", "D", alias_dir)
    remove_alias("A", alias_dir)
    assert "A" not in load_aliases(alias_dir)
    assert "C" in load_aliases(alias_dir)


# ---------------------------------------------------------------------------
# list_aliases
# ---------------------------------------------------------------------------

def test_list_aliases_empty_when_no_file(alias_dir):
    assert list_aliases(alias_dir) == []


def test_list_aliases_sorted(alias_dir):
    save_alias("Z_KEY", "A", alias_dir)
    save_alias("A_KEY", "B", alias_dir)
    assert list_aliases(alias_dir) == ["A_KEY", "Z_KEY"]


# ---------------------------------------------------------------------------
# apply_aliases
# ---------------------------------------------------------------------------

def test_apply_aliases_renames_key():
    env = {"DB_HOST": "localhost"}
    result = apply_aliases(env, {"DB_HOST": "DATABASE_HOST"})
    assert "DATABASE_HOST" in result
    assert "DB_HOST" not in result
    assert result["DATABASE_HOST"] == "localhost"


def test_apply_aliases_leaves_unmatched_keys():
    env = {"APP_PORT": "8080", "DB_HOST": "localhost"}
    result = apply_aliases(env, {"DB_HOST": "DATABASE_HOST"})
    assert result["APP_PORT"] == "8080"


def test_apply_aliases_does_not_mutate_original():
    env = {"KEY": "val"}
    apply_aliases(env, {"KEY": "OTHER"})
    assert "KEY" in env


def test_apply_aliases_raises_on_non_dict():
    with pytest.raises(TypeError):
        apply_aliases("not-a-dict", {})


def test_apply_aliases_empty_aliases_is_noop():
    env = {"A": "1", "B": "2"}
    assert apply_aliases(env, {}) == env
