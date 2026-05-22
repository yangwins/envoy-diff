"""Integration tests: masking interacts correctly with differ."""

import pytest
from envoy_diff.differ import diff_envs
from envoy_diff.masker import MASK_VALUE


def test_diff_masks_sensitive_values_in_changed():
    base = {"DB_PASSWORD": "old_secret", "HOST": "prod.example.com"}
    target = {"DB_PASSWORD": "new_secret", "HOST": "stg.example.com"}
    result = diff_envs(base, target, mask=True)
    # Both sides of the changed tuple should be masked
    old_val, new_val = result.changed["DB_PASSWORD"]
    assert old_val == MASK_VALUE
    assert new_val == MASK_VALUE
    # Non-sensitive key should still show real values
    old_host, new_host = result.changed["HOST"]
    assert old_host == "prod.example.com"
    assert new_host == "stg.example.com"


def test_diff_masks_sensitive_values_in_added():
    base = {"HOST": "prod.example.com"}
    target = {"HOST": "prod.example.com", "API_KEY": "sk-live-1234"}
    result = diff_envs(base, target, mask=True)
    assert result.added["API_KEY"] == MASK_VALUE


def test_diff_masks_sensitive_values_in_removed():
    base = {"HOST": "prod.example.com", "API_KEY": "sk-live-1234"}
    target = {"HOST": "prod.example.com"}
    result = diff_envs(base, target, mask=True)
    assert result.removed["API_KEY"] == MASK_VALUE


def test_diff_without_mask_shows_real_values():
    base = {"DB_PASSWORD": "old_secret"}
    target = {"DB_PASSWORD": "new_secret"}
    result = diff_envs(base, target, mask=False)
    old_val, new_val = result.changed["DB_PASSWORD"]
    assert old_val == "old_secret"
    assert new_val == "new_secret"


def test_diff_mask_with_show_length():
    base = {"API_KEY": "short"}
    target = {"API_KEY": "a-much-longer-key"}
    result = diff_envs(base, target, mask=True, show_length=True)
    old_val, new_val = result.changed["API_KEY"]
    assert "5" in old_val
    assert "17" in new_val


def test_diff_identical_masked_values_treated_as_unchanged():
    env = {"DB_PASSWORD": "same_secret", "HOST": "localhost"}
    result = diff_envs(env, env.copy(), mask=True)
    # With masking both become ***, so they appear unchanged
    assert "DB_PASSWORD" in result.unchanged
    assert "HOST" in result.unchanged
