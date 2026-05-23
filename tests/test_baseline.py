"""Unit tests for envoy_diff.baseline."""

from __future__ import annotations

import pytest
from pathlib import Path

from envoy_diff.baseline import (
    baseline_path,
    save_baseline,
    load_baseline,
    baseline_exists,
    clear_baseline,
)


@pytest.fixture()
def tmp_bl(tmp_path: Path) -> Path:
    """Return a path inside tmp_path that does not yet exist."""
    return tmp_path / ".envoy_baseline.json"


ENV: dict[str, str] = {"APP_ENV": "staging", "DB_HOST": "db.local", "PORT": "8080"}


def test_baseline_path_default_is_cwd():
    p = baseline_path()
    assert p.name == ".envoy_baseline.json"
    assert p.parent == Path.cwd()


def test_baseline_path_custom_directory(tmp_path):
    p = baseline_path(tmp_path)
    assert p == tmp_path / ".envoy_baseline.json"


def test_save_baseline_creates_file(tmp_bl):
    save_baseline(ENV, path=tmp_bl)
    assert tmp_bl.exists()


def test_save_baseline_returns_path(tmp_bl):
    result = save_baseline(ENV, path=tmp_bl)
    assert result == tmp_bl.resolve()


def test_save_baseline_raises_if_exists(tmp_bl):
    save_baseline(ENV, path=tmp_bl)
    with pytest.raises(FileExistsError):
        save_baseline(ENV, path=tmp_bl)


def test_save_baseline_overwrite(tmp_bl):
    save_baseline(ENV, path=tmp_bl)
    new_env = {"APP_ENV": "production"}
    save_baseline(new_env, path=tmp_bl, overwrite=True)
    loaded = load_baseline(path=tmp_bl)
    assert loaded["APP_ENV"] == "production"


def test_load_baseline_returns_env(tmp_bl):
    save_baseline(ENV, path=tmp_bl)
    loaded = load_baseline(path=tmp_bl)
    assert loaded == ENV


def test_load_baseline_raises_if_missing(tmp_bl):
    with pytest.raises(FileNotFoundError):
        load_baseline(path=tmp_bl)


def test_baseline_exists_false_when_missing(tmp_bl):
    assert baseline_exists(path=tmp_bl) is False


def test_baseline_exists_true_after_save(tmp_bl):
    save_baseline(ENV, path=tmp_bl)
    assert baseline_exists(path=tmp_bl) is True


def test_clear_baseline_removes_file(tmp_bl):
    save_baseline(ENV, path=tmp_bl)
    result = clear_baseline(path=tmp_bl)
    assert result is True
    assert not tmp_bl.exists()


def test_clear_baseline_returns_false_when_missing(tmp_bl):
    assert clear_baseline(path=tmp_bl) is False
