"""Tests for envoy_diff.annotator."""

import json
import pytest
from pathlib import Path

from envoy_diff.annotator import (
    _annotations_path,
    annotate_diff,
    delete_annotation,
    load_annotations,
    save_annotation,
)


@pytest.fixture()
def ann_dir(tmp_path: Path) -> str:
    return str(tmp_path)


def test_annotations_path_default_is_cwd():
    p = _annotations_path()
    assert p.name == ".envoy_annotations.json"
    assert p.parent == Path.cwd()


def test_annotations_path_custom_directory(ann_dir):
    p = _annotations_path(ann_dir)
    assert p.parent == Path(ann_dir)


def test_load_annotations_empty_when_no_file(ann_dir):
    result = load_annotations(ann_dir)
    assert result == {}


def test_save_annotation_creates_file(ann_dir):
    save_annotation("DB_HOST", "Primary database hostname", ann_dir)
    path = Path(ann_dir) / ".envoy_annotations.json"
    assert path.exists()


def test_save_annotation_returns_resolved_path(ann_dir):
    p = save_annotation("API_KEY", "Third-party API key", ann_dir)
    assert isinstance(p, Path)
    assert p.is_absolute()


def test_save_annotation_stores_note(ann_dir):
    save_annotation("REDIS_URL", "Cache layer URL", ann_dir)
    annotations = load_annotations(ann_dir)
    assert annotations["REDIS_URL"] == "Cache layer URL"


def test_save_annotation_overwrites_existing(ann_dir):
    save_annotation("PORT", "old note", ann_dir)
    save_annotation("PORT", "new note", ann_dir)
    annotations = load_annotations(ann_dir)
    assert annotations["PORT"] == "new note"


def test_save_multiple_annotations(ann_dir):
    save_annotation("A", "note a", ann_dir)
    save_annotation("B", "note b", ann_dir)
    annotations = load_annotations(ann_dir)
    assert annotations == {"A": "note a", "B": "note b"}


def test_delete_annotation_returns_true_when_exists(ann_dir):
    save_annotation("SECRET", "sensitive", ann_dir)
    assert delete_annotation("SECRET", ann_dir) is True


def test_delete_annotation_removes_key(ann_dir):
    save_annotation("SECRET", "sensitive", ann_dir)
    delete_annotation("SECRET", ann_dir)
    assert "SECRET" not in load_annotations(ann_dir)


def test_delete_annotation_returns_false_when_missing(ann_dir):
    assert delete_annotation("NONEXISTENT", ann_dir) is False


def test_annotate_diff_returns_only_annotated_keys(ann_dir):
    save_annotation("DB_HOST", "database host", ann_dir)
    save_annotation("SECRET", "secret key", ann_dir)
    diff_keys = {"DB_HOST": "changed", "PORT": "added"}
    result = annotate_diff(diff_keys, ann_dir)
    assert result == {"DB_HOST": "database host"}


def test_annotate_diff_empty_when_no_overlap(ann_dir):
    save_annotation("OTHER_KEY", "some note", ann_dir)
    result = annotate_diff({"DB_HOST": "changed"}, ann_dir)
    assert result == {}


def test_annotate_diff_empty_diff_returns_empty(ann_dir):
    save_annotation("DB_HOST", "note", ann_dir)
    assert annotate_diff({}, ann_dir) == {}


def test_load_annotations_raises_on_invalid_json(ann_dir):
    path = Path(ann_dir) / ".envoy_annotations.json"
    path.write_text("[1, 2, 3]\n", encoding="utf-8")
    with pytest.raises(ValueError, match="JSON object"):
        load_annotations(ann_dir)
