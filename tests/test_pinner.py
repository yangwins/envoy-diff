"""Unit tests for envoy_diff.pinner."""
import json
import pytest
from pathlib import Path

from envoy_diff.pinner import (
    PinViolation,
    PinResult,
    check_pins,
    load_pins,
    save_pin,
    remove_pin,
    _pins_path,
)


# ---------------------------------------------------------------------------
# PinViolation / PinResult
# ---------------------------------------------------------------------------

def test_pin_violation_as_dict():
    v = PinViolation(key="FOO", expected="bar", actual="baz")
    assert v.as_dict() == {"key": "FOO", "expected": "bar", "actual": "baz"}


def test_pin_result_passed_when_no_violations():
    assert PinResult().passed is True


def test_pin_result_failed_when_violations():
    v = PinViolation(key="X", expected="1", actual="2")
    assert PinResult(violations=[v]).passed is False


def test_pin_result_as_dict_structure():
    result = PinResult()
    d = result.as_dict()
    assert d["passed"] is True
    assert d["violations"] == []


# ---------------------------------------------------------------------------
# check_pins
# ---------------------------------------------------------------------------

def test_check_pins_passes_when_all_match():
    env = {"FOO": "bar", "BAZ": "qux"}
    result = check_pins(env, {"FOO": "bar"})
    assert result.passed


def test_check_pins_detects_wrong_value():
    env = {"FOO": "wrong"}
    result = check_pins(env, {"FOO": "expected"})
    assert not result.passed
    assert result.violations[0].key == "FOO"
    assert result.violations[0].expected == "expected"
    assert result.violations[0].actual == "wrong"


def test_check_pins_detects_missing_key():
    result = check_pins({}, {"MISSING": "value"})
    assert not result.passed
    assert result.violations[0].actual is None


def test_check_pins_empty_pins_always_passes():
    assert check_pins({"FOO": "bar"}, {}).passed


def test_check_pins_multiple_violations():
    env = {"A": "1", "B": "2"}
    result = check_pins(env, {"A": "X", "B": "Y"})
    assert len(result.violations) == 2


# ---------------------------------------------------------------------------
# load_pins / save_pin / remove_pin
# ---------------------------------------------------------------------------

def test_load_pins_empty_when_no_file(tmp_path):
    assert load_pins(tmp_path) == {}


def test_save_pin_creates_file(tmp_path):
    save_pin("KEY", "val", tmp_path)
    assert _pins_path(tmp_path).exists()


def test_save_pin_stores_value(tmp_path):
    save_pin("DB_HOST", "localhost", tmp_path)
    pins = load_pins(tmp_path)
    assert pins["DB_HOST"] == "localhost"


def test_save_pin_overwrites_existing(tmp_path):
    save_pin("KEY", "old", tmp_path)
    save_pin("KEY", "new", tmp_path)
    assert load_pins(tmp_path)["KEY"] == "new"


def test_remove_pin_returns_true_when_existed(tmp_path):
    save_pin("KEY", "val", tmp_path)
    assert remove_pin("KEY", tmp_path) is True


def test_remove_pin_returns_false_when_absent(tmp_path):
    assert remove_pin("GHOST", tmp_path) is False


def test_remove_pin_deletes_key(tmp_path):
    save_pin("A", "1", tmp_path)
    save_pin("B", "2", tmp_path)
    remove_pin("A", tmp_path)
    pins = load_pins(tmp_path)
    assert "A" not in pins
    assert "B" in pins


def test_load_pins_raises_on_invalid_json(tmp_path):
    _pins_path(tmp_path).write_text("[1, 2, 3]\n")
    with pytest.raises(ValueError):
        load_pins(tmp_path)
