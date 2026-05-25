"""Tests for envoy_diff.differ_patch."""

import pytest

from envoy_diff.differ_patch import (
    EnvPatch,
    PatchOperation,
    apply_patch,
    build_patch,
)


# ---------------------------------------------------------------------------
# PatchOperation
# ---------------------------------------------------------------------------

def test_patch_operation_as_dict_add():
    op = PatchOperation(op="add", key="FOO", value="bar")
    d = op.as_dict()
    assert d["op"] == "add"
    assert d["key"] == "FOO"
    assert d["value"] == "bar"
    assert "old_value" not in d


def test_patch_operation_as_dict_remove():
    op = PatchOperation(op="remove", key="FOO", old_value="bar")
    d = op.as_dict()
    assert d["op"] == "remove"
    assert d["old_value"] == "bar"
    assert "value" not in d


def test_patch_operation_as_dict_replace():
    op = PatchOperation(op="replace", key="FOO", value="new", old_value="old")
    d = op.as_dict()
    assert d["value"] == "new"
    assert d["old_value"] == "old"


# ---------------------------------------------------------------------------
# EnvPatch
# ---------------------------------------------------------------------------

def test_env_patch_is_empty_when_no_operations():
    assert EnvPatch().is_empty()


def test_env_patch_not_empty_when_has_operations():
    patch = EnvPatch(operations=[PatchOperation(op="add", key="X", value="1")])
    assert not patch.is_empty()


def test_env_patch_as_dict_contains_operations_list():
    patch = EnvPatch(operations=[PatchOperation(op="add", key="X", value="1")])
    d = patch.as_dict()
    assert "operations" in d
    assert len(d["operations"]) == 1


# ---------------------------------------------------------------------------
# build_patch
# ---------------------------------------------------------------------------

def test_build_patch_empty_envs_produces_empty_patch():
    patch = build_patch({}, {})
    assert patch.is_empty()


def test_build_patch_detects_added_key():
    patch = build_patch({}, {"NEW": "1"})
    assert len(patch.operations) == 1
    assert patch.operations[0].op == "add"
    assert patch.operations[0].key == "NEW"


def test_build_patch_detects_removed_key():
    patch = build_patch({"OLD": "1"}, {})
    assert patch.operations[0].op == "remove"
    assert patch.operations[0].key == "OLD"


def test_build_patch_detects_changed_key():
    patch = build_patch({"K": "old"}, {"K": "new"})
    assert patch.operations[0].op == "replace"
    assert patch.operations[0].old_value == "old"
    assert patch.operations[0].value == "new"


def test_build_patch_unchanged_keys_produce_no_operations():
    patch = build_patch({"A": "1", "B": "2"}, {"A": "1", "B": "2"})
    assert patch.is_empty()


# ---------------------------------------------------------------------------
# apply_patch
# ---------------------------------------------------------------------------

def test_apply_patch_add_key():
    result = apply_patch({}, EnvPatch([PatchOperation(op="add", key="X", value="1")]))
    assert result["X"] == "1"


def test_apply_patch_remove_key():
    result = apply_patch({"X": "1"}, EnvPatch([PatchOperation(op="remove", key="X", old_value="1")]))
    assert "X" not in result


def test_apply_patch_replace_key():
    result = apply_patch({"X": "old"}, EnvPatch([PatchOperation(op="replace", key="X", value="new", old_value="old")]))
    assert result["X"] == "new"


def test_apply_patch_does_not_mutate_base():
    base = {"A": "1"}
    apply_patch(base, EnvPatch([PatchOperation(op="add", key="B", value="2")]))
    assert "B" not in base


def test_apply_patch_raises_on_add_existing_key():
    with pytest.raises(ValueError, match="already exists"):
        apply_patch({"X": "1"}, EnvPatch([PatchOperation(op="add", key="X", value="2")]))


def test_apply_patch_raises_on_remove_missing_key():
    with pytest.raises(ValueError, match="not found"):
        apply_patch({}, EnvPatch([PatchOperation(op="remove", key="X", old_value="1")]))


def test_apply_patch_raises_on_replace_missing_key():
    with pytest.raises(ValueError, match="not found"):
        apply_patch({}, EnvPatch([PatchOperation(op="replace", key="X", value="v", old_value="o")]))


def test_apply_patch_raises_on_unknown_op():
    with pytest.raises(ValueError, match="Unknown patch operation"):
        apply_patch({}, EnvPatch([PatchOperation(op="noop", key="X")]))
