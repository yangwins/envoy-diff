"""Tests for envoy_diff.archiver."""

import pytest

from envoy_diff.archiver import (
    _archive_path,
    archive_metadata,
    delete_archive,
    list_archives,
    load_archive,
    save_archive,
)


@pytest.fixture()
def arc_dir(tmp_path):
    return str(tmp_path)


def test_archive_path_default_is_cwd():
    p = _archive_path()
    assert p.name == ".envoy_archive.json"


def test_archive_path_custom_directory(arc_dir):
    p = _archive_path(arc_dir)
    assert p.parent == pytest.importorskip("pathlib").Path(arc_dir)


def test_list_archives_empty_when_no_file(arc_dir):
    assert list_archives(arc_dir) == []


def test_save_archive_creates_file(arc_dir):
    save_archive("v1", {"KEY": "val"}, directory=arc_dir)
    import pathlib
    assert (pathlib.Path(arc_dir) / ".envoy_archive.json").exists()


def test_save_archive_returns_resolved_path(arc_dir):
    path = save_archive("v1", {"A": "1"}, directory=arc_dir)
    assert path.is_absolute()


def test_save_archive_stores_env(arc_dir):
    save_archive("v1", {"FOO": "bar", "BAZ": "qux"}, directory=arc_dir)
    env = load_archive("v1", directory=arc_dir)
    assert env == {"FOO": "bar", "BAZ": "qux"}


def test_save_archive_coerces_values_to_str(arc_dir):
    save_archive("v1", {"PORT": 8080}, directory=arc_dir)  # type: ignore[arg-type]
    env = load_archive("v1", directory=arc_dir)
    assert env["PORT"] == "8080"


def test_save_archive_raises_on_duplicate(arc_dir):
    save_archive("v1", {"A": "1"}, directory=arc_dir)
    with pytest.raises(KeyError, match="v1"):
        save_archive("v1", {"A": "2"}, directory=arc_dir)


def test_save_archive_overwrite_replaces_entry(arc_dir):
    save_archive("v1", {"A": "1"}, directory=arc_dir)
    save_archive("v1", {"A": "2"}, directory=arc_dir, overwrite=True)
    env = load_archive("v1", directory=arc_dir)
    assert env["A"] == "2"


def test_list_archives_sorted(arc_dir):
    save_archive("zebra", {}, directory=arc_dir)
    save_archive("alpha", {}, directory=arc_dir)
    assert list_archives(arc_dir) == ["alpha", "zebra"]


def test_load_archive_raises_when_missing(arc_dir):
    with pytest.raises(KeyError, match="ghost"):
        load_archive("ghost", directory=arc_dir)


def test_delete_archive_returns_true_when_exists(arc_dir):
    save_archive("v1", {"X": "y"}, directory=arc_dir)
    assert delete_archive("v1", directory=arc_dir) is True


def test_delete_archive_returns_false_when_missing(arc_dir):
    assert delete_archive("nope", directory=arc_dir) is False


def test_delete_archive_removes_entry(arc_dir):
    save_archive("v1", {"X": "y"}, directory=arc_dir)
    delete_archive("v1", directory=arc_dir)
    assert "v1" not in list_archives(arc_dir)


def test_archive_metadata_contains_saved_at(arc_dir):
    save_archive("v1", {"K": "v"}, directory=arc_dir)
    meta = archive_metadata("v1", directory=arc_dir)
    assert "saved_at" in meta
    assert isinstance(meta["saved_at"], float)


def test_archive_metadata_raises_when_missing(arc_dir):
    with pytest.raises(KeyError):
        archive_metadata("missing", directory=arc_dir)
