"""Unit tests for envoy_diff.tagger."""

import json
import pytest
from pathlib import Path

from envoy_diff.tagger import (
    _tags_path,
    load_tags,
    save_tag,
    remove_tag,
    keys_for_tag,
    tags_for_key,
)


@pytest.fixture()
def tag_dir(tmp_path):
    return str(tmp_path)


def test_tags_path_default_is_cwd():
    p = _tags_path()
    assert p.name == ".envoy_tags.json"
    assert p.parent == Path.cwd()


def test_tags_path_custom_directory(tag_dir):
    p = _tags_path(tag_dir)
    assert p.parent == Path(tag_dir)


def test_load_tags_empty_when_no_file(tag_dir):
    assert load_tags(tag_dir) == {}


def test_save_tag_creates_file(tag_dir):
    save_tag("DB_HOST", "database", tag_dir)
    assert (Path(tag_dir) / ".envoy_tags.json").exists()


def test_save_tag_stores_tag(tag_dir):
    save_tag("DB_HOST", "database", tag_dir)
    tags = load_tags(tag_dir)
    assert "database" in tags["DB_HOST"]


def test_save_tag_multiple_tags_on_same_key(tag_dir):
    save_tag("API_KEY", "secret", tag_dir)
    save_tag("API_KEY", "external", tag_dir)
    tags = load_tags(tag_dir)
    assert set(tags["API_KEY"]) == {"secret", "external"}


def test_save_tag_is_idempotent(tag_dir):
    save_tag("DB_HOST", "database", tag_dir)
    save_tag("DB_HOST", "database", tag_dir)
    tags = load_tags(tag_dir)
    assert tags["DB_HOST"].count("database") == 1


def test_remove_tag_removes_existing(tag_dir):
    save_tag("DB_HOST", "database", tag_dir)
    remove_tag("DB_HOST", "database", tag_dir)
    tags = load_tags(tag_dir)
    assert "DB_HOST" not in tags


def test_remove_tag_noop_when_tag_missing(tag_dir):
    save_tag("DB_HOST", "database", tag_dir)
    remove_tag("DB_HOST", "nonexistent", tag_dir)  # should not raise
    tags = load_tags(tag_dir)
    assert "database" in tags["DB_HOST"]


def test_remove_tag_noop_when_key_missing(tag_dir):
    remove_tag("MISSING_KEY", "database", tag_dir)  # should not raise


def test_keys_for_tag_returns_matching_keys(tag_dir):
    save_tag("DB_HOST", "database", tag_dir)
    save_tag("DB_PORT", "database", tag_dir)
    save_tag("API_KEY", "secret", tag_dir)
    result = keys_for_tag("database", tag_dir)
    assert set(result) == {"DB_HOST", "DB_PORT"}


def test_keys_for_tag_empty_when_no_match(tag_dir):
    save_tag("DB_HOST", "database", tag_dir)
    assert keys_for_tag("secret", tag_dir) == []


def test_tags_for_key_returns_tags(tag_dir):
    save_tag("DB_HOST", "database", tag_dir)
    save_tag("DB_HOST", "infra", tag_dir)
    assert set(tags_for_key("DB_HOST", tag_dir)) == {"database", "infra"}


def test_tags_for_key_empty_when_key_missing(tag_dir):
    assert tags_for_key("UNKNOWN", tag_dir) == []


def test_load_tags_raises_on_invalid_file(tag_dir):
    path = Path(tag_dir) / ".envoy_tags.json"
    path.write_text(json.dumps(["not", "a", "dict"]), encoding="utf-8")
    with pytest.raises(ValueError, match="JSON object"):
        load_tags(tag_dir)
