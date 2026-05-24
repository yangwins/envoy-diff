"""Tests for envoy_diff.templater."""

from __future__ import annotations

import pytest

from envoy_diff.templater import (
    DEFAULT_SUMMARY_TEMPLATE,
    build_report_context,
    render_template,
)


# ---------------------------------------------------------------------------
# render_template
# ---------------------------------------------------------------------------


def test_render_template_replaces_single_placeholder():
    result = render_template("Hello {{ name }}!", {"name": "world"})
    assert result == "Hello world!"


def test_render_template_replaces_multiple_placeholders():
    tmpl = "{{ a }} + {{ b }} = {{ c }}"
    result = render_template(tmpl, {"a": 1, "b": 2, "c": 3})
    assert result == "1 + 2 = 3"


def test_render_template_leaves_unknown_placeholder_intact():
    result = render_template("{{ known }} and {{ unknown }}", {"known": "yes"})
    assert result == "yes and {{ unknown }}"


def test_render_template_handles_whitespace_in_placeholder():
    result = render_template("{{  key  }}", {"key": "value"})
    assert result == "value"


def test_render_template_empty_context_leaves_template_unchanged():
    tmpl = "{{ foo }} bar"
    assert render_template(tmpl, {}) == tmpl


def test_render_template_empty_template_returns_empty_string():
    assert render_template("", {"x": 1}) == ""


def test_render_template_coerces_values_to_str():
    result = render_template("count={{ n }}", {"n": 42})
    assert result == "count=42"


def test_render_template_raises_on_non_str_template():
    with pytest.raises(TypeError, match="template must be a str"):
        render_template(123, {})  # type: ignore[arg-type]


def test_render_template_raises_on_non_dict_context():
    with pytest.raises(TypeError, match="context must be a dict"):
        render_template("{{ x }}", [])  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# build_report_context
# ---------------------------------------------------------------------------


def test_build_report_context_defaults():
    ctx = build_report_context()
    assert ctx["added"] == 0
    assert ctx["removed"] == 0
    assert ctx["changed"] == 0
    assert ctx["unchanged"] == 0
    assert ctx["total"] == 0


def test_build_report_context_total_is_sum():
    ctx = build_report_context(added=2, removed=1, changed=3, unchanged=5)
    assert ctx["total"] == 11


def test_build_report_context_labels():
    ctx = build_report_context(env_a_label="staging", env_b_label="prod")
    assert ctx["env_a"] == "staging"
    assert ctx["env_b"] == "prod"


def test_build_report_context_score_absent_by_default():
    ctx = build_report_context()
    assert "score" not in ctx


def test_build_report_context_score_rounded():
    ctx = build_report_context(score=3.14159)
    assert ctx["score"] == 3.14


# ---------------------------------------------------------------------------
# DEFAULT_SUMMARY_TEMPLATE integration
# ---------------------------------------------------------------------------


def test_default_summary_template_renders_correctly():
    ctx = build_report_context(
        env_a_label="staging",
        env_b_label="production",
        added=2,
        removed=1,
        changed=3,
        unchanged=10,
    )
    result = render_template(DEFAULT_SUMMARY_TEMPLATE, ctx)
    assert "staging" in result
    assert "production" in result
    assert "+2" in result
    assert "-1" in result
    assert "~3" in result
    assert "10 unchanged" in result
