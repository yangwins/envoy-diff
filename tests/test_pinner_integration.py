"""Integration tests: pinner working with loader and differ."""
from envoy_diff.pinner import check_pins, save_pin, load_pins
from envoy_diff.differ import diff_envs


def test_pin_passes_for_identical_envs(tmp_path):
    env = {"APP_ENV": "production", "PORT": "8080"}
    save_pin("APP_ENV", "production", tmp_path)
    pins = load_pins(tmp_path)
    result = check_pins(env, pins)
    assert result.passed


def test_pin_fails_when_env_changed(tmp_path):
    save_pin("APP_ENV", "production", tmp_path)
    env = {"APP_ENV": "staging"}
    pins = load_pins(tmp_path)
    result = check_pins(env, pins)
    assert not result.passed
    assert result.violations[0].key == "APP_ENV"


def test_pin_combined_with_diff(tmp_path):
    """Diff detects a change AND pin catches the same key being wrong."""
    staging = {"APP_ENV": "staging", "PORT": "8080"}
    production = {"APP_ENV": "production", "PORT": "8080"}
    save_pin("APP_ENV", "production", tmp_path)

    diff = diff_envs(staging, production)
    assert "APP_ENV" in diff.changed

    pins = load_pins(tmp_path)
    pin_result = check_pins(staging, pins)
    assert not pin_result.passed


def test_pin_unchanged_key_passes_after_diff(tmp_path):
    staging = {"PORT": "8080", "APP_ENV": "staging"}
    production = {"PORT": "8080", "APP_ENV": "production"}
    save_pin("PORT", "8080", tmp_path)

    pins = load_pins(tmp_path)
    # PORT is the same in both; check against production
    result = check_pins(production, pins)
    assert result.passed


def test_multiple_pins_partial_failure(tmp_path):
    save_pin("A", "1", tmp_path)
    save_pin("B", "2", tmp_path)
    env = {"A": "1", "B": "WRONG"}
    pins = load_pins(tmp_path)
    result = check_pins(env, pins)
    assert not result.passed
    assert len(result.violations) == 1
    assert result.violations[0].key == "B"


def test_empty_env_all_pins_fail(tmp_path):
    save_pin("X", "foo", tmp_path)
    save_pin("Y", "bar", tmp_path)
    pins = load_pins(tmp_path)
    result = check_pins({}, pins)
    assert len(result.violations) == 2
