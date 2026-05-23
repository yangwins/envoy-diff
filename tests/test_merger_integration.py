"""Integration tests: merger combined with differ and masker."""

from envoy_diff.differ import diff_envs
from envoy_diff.masker import mask_env
from envoy_diff.merger import MergeStrategy, merge_envs


def test_merge_then_diff_shows_no_changes_when_identical():
    base = {"A": "1", "B": "2"}
    override = {"A": "1", "B": "2"}
    merged = merge_envs(base, override)
    result = diff_envs(base, merged)
    assert result.changed == {}
    assert result.added == {}
    assert result.removed == {}


def test_merge_right_then_diff_shows_changed_key():
    base = {"A": "old", "B": "same"}
    override = {"A": "new", "B": "same"}
    merged = merge_envs(base, override, strategy=MergeStrategy.RIGHT)
    result = diff_envs(base, merged)
    assert "A" in result.changed
    assert result.changed["A"] == ("old", "new")


def test_merge_left_then_diff_shows_no_change_for_conflict():
    base = {"A": "original"}
    override = {"A": "ignored"}
    merged = merge_envs(base, override, strategy=MergeStrategy.LEFT)
    result = diff_envs(base, merged)
    assert result.changed == {}


def test_merge_adds_new_keys_visible_in_diff():
    base = {"EXISTING": "val"}
    override = {"NEW_KEY": "brand-new"}
    merged = merge_envs(base, override)
    result = diff_envs(base, merged)
    assert "NEW_KEY" in result.added


def test_merge_with_mask_hides_sensitive_values():
    base = {"DB_PASSWORD": "secret1", "HOST": "localhost"}
    override = {"DB_PASSWORD": "secret2", "HOST": "prod-host"}
    merged = merge_envs(base, override)
    masked_base = mask_env(base)
    masked_merged = mask_env(merged)
    result = diff_envs(masked_base, masked_merged)
    # password values should be masked, not raw secrets
    if "DB_PASSWORD" in result.changed:
        old_val, new_val = result.changed["DB_PASSWORD"]
        assert "secret" not in old_val
        assert "secret" not in new_val


def test_merge_prefix_limits_diff_scope():
    base = {"APP_HOST": "localhost", "DB_HOST": "db-old"}
    override = {"APP_HOST": "prod-host", "DB_HOST": "db-new"}
    # only merge APP_ prefix keys from override
    merged = merge_envs(base, override, prefix="APP_")
    result = diff_envs(base, merged)
    assert "APP_HOST" in result.changed
    assert "DB_HOST" not in result.changed
