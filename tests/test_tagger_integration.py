"""Integration tests: tagger interacting with differ and filter."""

import pytest

from envoy_diff.tagger import save_tag, keys_for_tag, tags_for_key
from envoy_diff.differ import diff_envs
from envoy_diff.filter import filter_env


@pytest.fixture()
def tag_dir(tmp_path):
    return str(tmp_path)


def test_tag_then_filter_by_tagged_keys(tag_dir):
    """Keys tagged 'critical' can be used to drive a filter operation."""
    env_a = {"DB_HOST": "localhost", "API_KEY": "abc", "LOG_LEVEL": "info"}
    env_b = {"DB_HOST": "prod-db", "API_KEY": "abc", "LOG_LEVEL": "debug"}

    save_tag("DB_HOST", "critical", tag_dir)
    save_tag("API_KEY", "critical", tag_dir)

    critical_keys = keys_for_tag("critical", tag_dir)
    filtered_a = filter_env(env_a, include=critical_keys)
    filtered_b = filter_env(env_b, include=critical_keys)

    result = diff_envs(filtered_a, filtered_b)
    changed_keys = {k for k, _, _ in result.changed}
    assert "DB_HOST" in changed_keys
    assert "LOG_LEVEL" not in changed_keys


def test_diff_unchanged_when_tagged_keys_same(tag_dir):
    env_a = {"DB_HOST": "same", "NOISE": "x"}
    env_b = {"DB_HOST": "same", "NOISE": "y"}

    save_tag("DB_HOST", "watch", tag_dir)
    watched = keys_for_tag("watch", tag_dir)

    result = diff_envs(
        filter_env(env_a, include=watched),
        filter_env(env_b, include=watched),
    )
    assert not result.changed
    assert not result.added
    assert not result.removed


def test_multiple_tags_per_key_visible_in_both_groups(tag_dir):
    save_tag("SECRET_KEY", "secret", tag_dir)
    save_tag("SECRET_KEY", "critical", tag_dir)

    assert "SECRET_KEY" in keys_for_tag("secret", tag_dir)
    assert "SECRET_KEY" in keys_for_tag("critical", tag_dir)
    assert set(tags_for_key("SECRET_KEY", tag_dir)) == {"secret", "critical"}


def test_tag_removed_key_no_longer_in_group(tag_dir):
    from envoy_diff.tagger import remove_tag

    save_tag("DB_HOST", "database", tag_dir)
    save_tag("DB_PORT", "database", tag_dir)
    remove_tag("DB_PORT", "database", tag_dir)

    db_keys = keys_for_tag("database", tag_dir)
    assert "DB_HOST" in db_keys
    assert "DB_PORT" not in db_keys


def test_diff_added_key_with_tag(tag_dir):
    """A key present only in env_b and tagged shows up as added in diff."""
    env_a = {"DB_HOST": "localhost"}
    env_b = {"DB_HOST": "localhost", "NEW_FEATURE_FLAG": "true"}

    save_tag("NEW_FEATURE_FLAG", "feature", tag_dir)
    feature_keys = keys_for_tag("feature", tag_dir)

    result = diff_envs(
        filter_env(env_a, include=list(env_b.keys())),
        filter_env(env_b, include=list(env_b.keys())),
    )
    added_keys = {k for k, _ in result.added}
    assert "NEW_FEATURE_FLAG" in added_keys
    assert "NEW_FEATURE_FLAG" in feature_keys
