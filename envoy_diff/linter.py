"""Lint environment variable keys for naming convention violations."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List

# Keys should be UPPER_SNAKE_CASE with optional leading underscore
_VALID_KEY_RE = re.compile(r'^[A-Z_][A-Z0-9_]*$')
_LEADING_DIGIT_RE = re.compile(r'^[0-9]')
_LOWERCASE_RE = re.compile(r'[a-z]')


@dataclass
class LintViolation:
    key: str
    reason: str

    def as_dict(self) -> Dict[str, str]:
        return {"key": self.key, "reason": self.reason}


@dataclass
class LintResult:
    violations: List[LintViolation] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.violations) == 0

    def as_dict(self) -> Dict:
        return {
            "passed": self.passed,
            "violation_count": len(self.violations),
            "violations": [v.as_dict() for v in self.violations],
        }


def _check_key(key: str) -> List[str]:
    """Return a list of reasons why *key* is invalid (empty means valid)."""
    reasons: List[str] = []
    if not key:
        reasons.append("key must not be empty")
        return reasons
    if _LEADING_DIGIT_RE.match(key):
        reasons.append("key must not start with a digit")
    if _LOWERCASE_RE.search(key):
        reasons.append("key contains lowercase letters; use UPPER_SNAKE_CASE")
    if not _VALID_KEY_RE.match(key):
        reasons.append("key contains invalid characters; only A-Z, 0-9, and _ are allowed")
    return reasons


def lint_env(env: Dict[str, str]) -> LintResult:
    """Lint all keys in *env* and return a :class:`LintResult`."""
    if not isinstance(env, dict):
        raise TypeError(f"env must be a dict, got {type(env).__name__}")
    violations: List[LintViolation] = []
    for key in env:
        for reason in _check_key(key):
            violations.append(LintViolation(key=key, reason=reason))
    return LintResult(violations=violations)


def lint_envs(*envs: Dict[str, str]) -> LintResult:
    """Lint multiple env dicts and aggregate all violations."""
    all_violations: List[LintViolation] = []
    for env in envs:
        all_violations.extend(lint_env(env).violations)
    return LintResult(violations=all_violations)
