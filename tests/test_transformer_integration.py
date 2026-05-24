"""Integration tests: transformer -> differ pipeline."""

from __future__ import annotations

from envoy_diff.differ import diff_envs
from envoy_diff.transformer import transform_env


def test_strip_prefix_makes_envs_comparable():
    """Two envs with different prefixes should show no diff after stripping."""
    staging = {"STG_HOST": "app.stg", "STG_PORT": "8080"}
    prod = {"PRD_HOST": "app.prd", "PRD_PORT": "8080"}

    t_staging = transform_env(staging, strip_prefix_str="STG_")
    t_prod = transform_env(prod, strip_prefix_str="PRD_")

    result = diff_envs(t_staging, t_prod)
    # HOST differs, PORT is the same
    assert "HOST" in result.changed
    assert "PORT" in result.unchanged


def test_value_substitution_hides_placeholder_diff():
    """Placeholder values normalised to empty string should not appear changed."""
    env_a = {"DB_URL": "<unset>"}
    env_b = {"DB_URL": ""}

    t_a = transform_env(env_a, value_substitutions={"<unset>": ""})
    t_b = transform_env(env_b)

    result = diff_envs(t_a, t_b)
    assert "DB_URL" in result.unchanged
    assert "DB_URL" not in result.changed


def test_rename_keys_aligns_different_naming_conventions():
    env_a = {"DATABASE_URL": "postgres://a"}
    env_b = {"DB_URL": "postgres://a"}

    t_a = transform_env(env_a, key_mapping={"DATABASE_URL": "DB_URL"})

    result = diff_envs(t_a, env_b)
    assert not result.changed
    assert "DB_URL" in result.unchanged


def test_transform_then_diff_detects_real_change():
    env_a = {"APP_HOST": "old.host"}
    env_b = {"APP_HOST": "new.host"}

    t_a = transform_env(env_a, strip_prefix_str="APP_")
    t_b = transform_env(env_b, strip_prefix_str="APP_")

    result = diff_envs(t_a, t_b)
    assert "HOST" in result.changed


def test_transform_empty_envs_produces_empty_diff():
    result = diff_envs(
        transform_env({}, strip_prefix_str="APP_"),
        transform_env({}, strip_prefix_str="APP_"),
    )
    assert not result.added
    assert not result.removed
    assert not result.changed
