"""Unit tests for envoy_diff.auditor."""
import json
import time
from pathlib import Path

import pytest

from envoy_diff.auditor import (
    AuditEntry,
    DEFAULT_AUDIT_FILE,
    clear_audit,
    load_audit,
    record,
)


@pytest.fixture()
def tmp_dir(tmp_path):
    return tmp_path


def test_record_creates_audit_file(tmp_dir):
    record("diff", "staging", "production", 1, 0, 0, directory=tmp_dir)
    assert (tmp_dir / DEFAULT_AUDIT_FILE).exists()


def test_record_returns_audit_entry(tmp_dir):
    entry = record("diff", "staging", "production", 1, 2, 3, directory=tmp_dir)
    assert isinstance(entry, AuditEntry)


def test_record_stores_operation(tmp_dir):
    entry = record("snapshot", "a", "b", 0, 0, 0, directory=tmp_dir)
    assert entry.operation == "snapshot"


def test_record_stores_counts(tmp_dir):
    entry = record("diff", "a", "b", 4, 3, 2, directory=tmp_dir)
    assert entry.added == 4
    assert entry.removed == 3
    assert entry.changed == 2


def test_record_stores_user(tmp_dir):
    entry = record("diff", "a", "b", 0, 0, 0, directory=tmp_dir, user="alice")
    assert entry.user == "alice"


def test_record_stores_tags(tmp_dir):
    entry = record("diff", "a", "b", 0, 0, 0, directory=tmp_dir, tags=["ci", "nightly"])
    assert "ci" in entry.tags
    assert "nightly" in entry.tags


def test_record_timestamp_is_recent(tmp_dir):
    before = time.time()
    entry = record("diff", "a", "b", 0, 0, 0, directory=tmp_dir)
    after = time.time()
    assert before <= entry.timestamp <= after


def test_load_audit_returns_empty_when_no_file(tmp_dir):
    entries = load_audit(directory=tmp_dir)
    assert entries == []


def test_load_audit_returns_recorded_entries(tmp_dir):
    record("diff", "a", "b", 1, 0, 0, directory=tmp_dir)
    record("diff", "a", "b", 0, 1, 0, directory=tmp_dir)
    entries = load_audit(directory=tmp_dir)
    assert len(entries) == 2


def test_load_audit_accumulates_entries(tmp_dir):
    for i in range(3):
        record("diff", "a", "b", i, 0, 0, directory=tmp_dir)
    entries = load_audit(directory=tmp_dir)
    assert len(entries) == 3


def test_audit_entry_as_dict_has_expected_keys(tmp_dir):
    entry = record("diff", "staging", "prod", 1, 2, 3, directory=tmp_dir)
    d = entry.as_dict()
    for key in ("timestamp", "operation", "source_a", "source_b", "added", "removed", "changed"):
        assert key in d


def test_clear_audit_removes_file(tmp_dir):
    record("diff", "a", "b", 0, 0, 0, directory=tmp_dir)
    clear_audit(directory=tmp_dir)
    assert not (tmp_dir / DEFAULT_AUDIT_FILE).exists()


def test_clear_audit_no_error_when_missing(tmp_dir):
    clear_audit(directory=tmp_dir)  # should not raise


def test_audit_file_is_valid_json(tmp_dir):
    record("diff", "a", "b", 1, 1, 1, directory=tmp_dir)
    raw = (tmp_dir / DEFAULT_AUDIT_FILE).read_text()
    parsed = json.loads(raw)
    assert isinstance(parsed, list)
