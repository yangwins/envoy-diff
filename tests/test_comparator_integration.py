"""Integration tests for comparator combined with masker and filter."""
from __future__ import annotations

import pytest

from envoy_diff.comparator import compare
from envoy_diff.masker import mask_env
from envoy_diff.filter import filter_env


def test_compare_after_masking_hides_sensitive_changed():
    left = {"DB_PASSWORD": "secret1", "HOST": "a"}
    right = {"DB_PASSWORD": "secret2", "HOST": "b"}
    masked_left = mask_env(left)
    masked_right = mask_env(right)
    result = compare(masked_left, masked_right, left_label="staging", right_label="prod")
    # password is masked so both sides look the same — no change detected
    assert "DB_PASSWORD" not in result.diff.changed
    # HOST change is still visible
    assert "HOST" in result.diff.changed


def test_compare_after_filter_limits_scope():
    left = {"APP_HOST": "a", "DB_HOST": "x", "APP_PORT": "80"}
    right = {"APP_HOST": "b", "DB_HOST": "x", "APP_PORT": "80"}
    filtered_left = filter_env(left, prefix="APP_")
    filtered_right = filter_env(right, prefix="APP_")
    result = compare(filtered_left, filtered_right)
    assert "DB_HOST" not in result.diff.unchanged
    assert "APP_HOST" in result.diff.changed


def test_compare_empty_envs_zero_score():
    result = compare({}, {})
    assert result.score.total == 0


def test_compare_high_churn_raises_score():
    left = {str(i): "old" for i in range(10)}
    right = {str(i): "new" for i in range(10)}
    result = compare(left, right)
    assert result.score.total > 0
    assert result.summary.changed == 10


def test_compare_as_dict_round_trips_labels():
    result = compare({"A": "1"}, {"A": "1"}, left_label="s", right_label="p")
    d = result.as_dict()
    assert d["context"]["left_label"] == "s"
    assert d["context"]["right_label"] == "p"
