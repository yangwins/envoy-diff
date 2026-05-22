"""Tests for envoy_diff.cli_filter_args module."""

import argparse

import pytest

from envoy_diff.cli_filter_args import add_filter_args, apply_filters


SAMPLE = {
    "APP_HOST": "localhost",
    "APP_PORT": "8080",
    "DB_HOST": "db.internal",
    "LOG_LEVEL": "INFO",
}


# ---------------------------------------------------------------------------
# add_filter_args
# ---------------------------------------------------------------------------


def _make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    add_filter_args(p)
    return p


def test_add_filter_args_adds_prefix():
    p = _make_parser()
    ns = p.parse_args(["--prefix", "APP_"])
    assert ns.prefix == "APP_"


def test_add_filter_args_adds_include():
    p = _make_parser()
    ns = p.parse_args(["--include", "APP_*", "DB_*"])
    assert ns.include == ["APP_*", "DB_*"]


def test_add_filter_args_adds_exclude():
    p = _make_parser()
    ns = p.parse_args(["--exclude", "LOG_*"])
    assert ns.exclude == ["LOG_*"]


def test_add_filter_args_adds_regex():
    p = _make_parser()
    ns = p.parse_args(["--regex", "^APP_"])
    assert ns.regex == "^APP_"


def test_add_filter_args_defaults_are_none():
    p = _make_parser()
    ns = p.parse_args([])
    assert ns.prefix is None
    assert ns.include is None
    assert ns.exclude is None
    assert ns.regex is None


# ---------------------------------------------------------------------------
# apply_filters
# ---------------------------------------------------------------------------


def test_apply_filters_no_filters():
    assert apply_filters(SAMPLE) == SAMPLE


def test_apply_filters_prefix():
    result = apply_filters(SAMPLE, prefix="APP_")
    assert set(result.keys()) == {"APP_HOST", "APP_PORT"}


def test_apply_filters_include():
    result = apply_filters(SAMPLE, include=["DB_*"])
    assert set(result.keys()) == {"DB_HOST"}


def test_apply_filters_exclude():
    result = apply_filters(SAMPLE, exclude=["LOG_*"])
    assert "LOG_LEVEL" not in result


def test_apply_filters_regex():
    result = apply_filters(SAMPLE, regex=r"HOST$")
    assert set(result.keys()) == {"APP_HOST", "DB_HOST"}


def test_apply_filters_prefix_and_regex_combined():
    result = apply_filters(SAMPLE, prefix="APP_", regex=r"PORT")
    assert set(result.keys()) == {"APP_PORT"}


def test_apply_filters_empty_env():
    assert apply_filters({}, prefix="APP_", include=["*"], regex=r".*") == {}
