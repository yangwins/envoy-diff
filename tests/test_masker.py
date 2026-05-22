"""Tests for envoy_diff.masker."""

import re
import pytest
from envoy_diff.masker import (
    is_sensitive,
    mask_value,
    mask_env,
    MASK_VALUE,
    DEFAULT_SENSITIVE_PATTERNS,
)


def test_is_sensitive_detects_password():
    assert is_sensitive("DB_PASSWORD") is True


def test_is_sensitive_detects_token():
    assert is_sensitive("GITHUB_TOKEN") is True


def test_is_sensitive_detects_api_key():
    assert is_sensitive("STRIPE_API_KEY") is True


def test_is_sensitive_detects_secret():
    assert is_sensitive("APP_SECRET") is True


def test_is_sensitive_detects_auth():
    assert is_sensitive("OAUTH_AUTH_TOKEN") is True


def test_is_sensitive_returns_false_for_plain_key():
    assert is_sensitive("DATABASE_HOST") is False


def test_is_sensitive_returns_false_for_port():
    assert is_sensitive("PORT") is False


def test_is_sensitive_case_insensitive():
    assert is_sensitive("db_password") is True
    assert is_sensitive("DB_PASSWORD") is True


def test_is_sensitive_custom_patterns():
    patterns = [re.compile(r"custom", re.IGNORECASE)]
    assert is_sensitive("MY_CUSTOM_VAR", patterns=patterns) is True
    assert is_sensitive("DB_PASSWORD", patterns=patterns) is False


def test_mask_value_returns_mask():
    assert mask_value("super-secret-value") == MASK_VALUE


def test_mask_value_show_length():
    result = mask_value("abc", show_length=True)
    assert "3" in result
    assert MASK_VALUE in result


def test_mask_env_masks_sensitive_keys():
    env = {"DB_PASSWORD": "hunter2", "HOST": "localhost"}
    result = mask_env(env)
    assert result["DB_PASSWORD"] == MASK_VALUE
    assert result["HOST"] == "localhost"


def test_mask_env_does_not_mutate_original():
    env = {"DB_PASSWORD": "hunter2", "HOST": "localhost"}
    mask_env(env)
    assert env["DB_PASSWORD"] == "hunter2"


def test_mask_env_show_length():
    env = {"API_KEY": "12345"}
    result = mask_env(env, show_length=True)
    assert "5" in result["API_KEY"]


def test_mask_env_empty():
    assert mask_env({}) == {}


def test_mask_env_all_safe():
    env = {"HOST": "localhost", "PORT": "8080"}
    assert mask_env(env) == env
