"""Integration tests: aliaser + differ + masker."""
from __future__ import annotations

from envoy_diff.aliaser import apply_aliases, load_aliases, save_alias
from envoy_diff.differ import diff_envs
from envoy_diff.masker import mask_env


def test_alias_makes_renamed_key_appear_unchanged():
    """Renaming a key via alias before diffing should yield no change."""
    staging = {"DB_HOST": "db.staging.internal"}
    production = {"DATABASE_HOST": "db.staging.internal"}

    aliases = {"DB_HOST": "DATABASE_HOST"}
    normalised_staging = apply_aliases(staging, aliases)

    result = diff_envs(normalised_staging, production)
    assert result.unchanged == {"DATABASE_HOST": "db.staging.internal"}
    assert result.added == {}
    assert result.removed == {}
    assert result.changed == {}


def test_alias_exposes_real_value_change():
    staging = {"DB_HOST": "db.staging.internal"}
    production = {"DATABASE_HOST": "db.prod.internal"}

    aliases = {"DB_HOST": "DATABASE_HOST"}
    normalised_staging = apply_aliases(staging, aliases)

    result = diff_envs(normalised_staging, production)
    assert "DATABASE_HOST" in result.changed


def test_alias_without_match_shows_as_removed_and_added():
    staging = {"DB_HOST": "localhost"}
    production = {"DATABASE_HOST": "localhost"}

    # No aliases applied – keys are different
    result = diff_envs(staging, production)
    assert "DB_HOST" in result.removed
    assert "DATABASE_HOST" in result.added


def test_alias_combined_with_mask_hides_sensitive_renamed_key():
    staging = {"DB_PASSWORD": "secret123"}
    production = {"DATABASE_PASSWORD": "secret123"}

    aliases = {"DB_PASSWORD": "DATABASE_PASSWORD"}
    normalised = apply_aliases(staging, aliases)
    masked = mask_env(normalised)

    result = diff_envs(masked, production)
    # Value in staging is masked so it differs from production
    assert "DATABASE_PASSWORD" in result.changed


def test_round_trip_save_load_and_apply(tmp_path):
    d = str(tmp_path)
    save_alias("OLD_KEY", "NEW_KEY", d)
    aliases = load_aliases(d)

    env = {"OLD_KEY": "value", "UNRELATED": "other"}
    result = apply_aliases(env, aliases)

    assert result["NEW_KEY"] == "value"
    assert result["UNRELATED"] == "other"
    assert "OLD_KEY" not in result
