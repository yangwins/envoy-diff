"""Integration tests for differ_patch: round-trip and composition with other modules."""

from envoy_diff.differ import diff_envs
from envoy_diff.differ_patch import apply_patch, build_patch
from envoy_diff.masker import mask_env
from envoy_diff.normalizer import normalize_env


# ---------------------------------------------------------------------------
# Round-trip
# ---------------------------------------------------------------------------

def test_round_trip_apply_patch_produces_target():
    base = {"A": "1", "B": "2", "C": "3"}
    target = {"A": "1", "B": "changed", "D": "4"}
    patch = build_patch(base, target)
    result = apply_patch(base, patch)
    assert result == target


def test_round_trip_identical_envs_no_ops():
    env = {"X": "1", "Y": "2"}
    patch = build_patch(env, env)
    assert patch.is_empty()
    assert apply_patch(env, patch) == env


def test_round_trip_empty_to_populated():
    target = {"A": "1", "B": "2"}
    patch = build_patch({}, target)
    result = apply_patch({}, patch)
    assert result == target


def test_round_trip_populated_to_empty():
    base = {"A": "1", "B": "2"}
    patch = build_patch(base, {})
    result = apply_patch(base, patch)
    assert result == {}


# ---------------------------------------------------------------------------
# Composition with differ
# ---------------------------------------------------------------------------

def test_patch_then_diff_shows_no_changes():
    base = {"A": "1", "B": "old"}
    target = {"A": "1", "B": "new", "C": "3"}
    patch = build_patch(base, target)
    patched = apply_patch(base, patch)
    diff = diff_envs(patched, target)
    assert not diff.has_differences()


# ---------------------------------------------------------------------------
# Composition with normalizer
# ---------------------------------------------------------------------------

def test_patch_after_normalize_round_trips_correctly():
    base = normalize_env({"app_host": " localhost ", "app_port": "8080"})
    target = normalize_env({"app_host": " remotehost ", "app_port": "8080"})
    patch = build_patch(base, target)
    result = apply_patch(base, patch)
    assert result == target


# ---------------------------------------------------------------------------
# Composition with masker (patch keys unaffected by masking)
# ---------------------------------------------------------------------------

def test_patch_operations_keys_not_affected_by_mask():
    base = {"DB_PASSWORD": "secret1", "HOST": "localhost"}
    target = {"DB_PASSWORD": "secret2", "HOST": "remotehost"}
    patch = build_patch(base, target)
    # Keys in the patch should be the real key names regardless of masking
    keys_in_patch = {op.key for op in patch.operations}
    assert "DB_PASSWORD" in keys_in_patch
    assert "HOST" in keys_in_patch


def test_patch_as_dict_is_serialisable():
    import json
    base = {"A": "1"}
    target = {"A": "2", "B": "3"}
    patch = build_patch(base, target)
    # Should not raise
    serialised = json.dumps(patch.as_dict())
    data = json.loads(serialised)
    assert "operations" in data
    assert len(data["operations"]) == 2
