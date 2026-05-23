"""Integration tests for auditor combined with differ and summarizer."""
from pathlib import Path

import pytest

from envoy_diff.auditor import clear_audit, load_audit, record
from envoy_diff.differ import diff_envs
from envoy_diff.summarizer import summarize


@pytest.fixture()
def tmp_dir(tmp_path):
    return tmp_path


def _record_from_envs(env_a, env_b, directory):
    result = diff_envs(env_a, env_b)
    summary = summarize(result)
    return record(
        operation="diff",
        source_a="staging",
        source_b="production",
        added=summary.added,
        removed=summary.removed,
        changed=summary.changed,
        directory=directory,
    )


def test_audit_records_no_changes(tmp_dir):
    env = {"KEY": "val"}
    entry = _record_from_envs(env, env, tmp_dir)
    assert entry.added == 0
    assert entry.removed == 0
    assert entry.changed == 0


def test_audit_records_added_key(tmp_dir):
    entry = _record_from_envs({}, {"NEW": "1"}, tmp_dir)
    assert entry.added == 1


def test_audit_records_removed_key(tmp_dir):
    entry = _record_from_envs({"OLD": "1"}, {}, tmp_dir)
    assert entry.removed == 1


def test_audit_records_changed_key(tmp_dir):
    entry = _record_from_envs({"K": "a"}, {"K": "b"}, tmp_dir)
    assert entry.changed == 1


def test_multiple_diffs_accumulate_in_log(tmp_dir):
    _record_from_envs({"A": "1"}, {"A": "2"}, tmp_dir)
    _record_from_envs({}, {"B": "1"}, tmp_dir)
    entries = load_audit(directory=tmp_dir)
    assert len(entries) == 2


def test_audit_log_cleared_between_runs(tmp_dir):
    _record_from_envs({"A": "1"}, {"A": "2"}, tmp_dir)
    clear_audit(directory=tmp_dir)
    _record_from_envs({}, {"B": "1"}, tmp_dir)
    entries = load_audit(directory=tmp_dir)
    assert len(entries) == 1
