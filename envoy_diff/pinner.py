"""Pin specific environment variable keys to expected values.

A 'pin' asserts that a given key must equal a specific value in the
environment being diffed.  Violations are reported as a list of
``PinViolation`` named-tuples.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


@dataclass
class PinViolation:
    key: str
    expected: str
    actual: str | None  # None means the key is absent

    def as_dict(self) -> dict:
        return {"key": self.key, "expected": self.expected, "actual": self.actual}


@dataclass
class PinResult:
    violations: List[PinViolation] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.violations) == 0

    def as_dict(self) -> dict:
        return {
            "passed": self.passed,
            "violations": [v.as_dict() for v in self.violations],
        }


def _pins_path(directory: str | Path = ".") -> Path:
    return Path(directory) / ".envoy_pins.json"


def _load_pins_file(path: Path) -> Dict[str, str]:
    if not path.exists():
        return {}
    with path.open() as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"Pins file must contain a JSON object, got {type(data)}")
    return {str(k): str(v) for k, v in data.items()}


def _save_pins_file(path: Path, pins: Dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump(pins, fh, indent=2)
        fh.write("\n")


def load_pins(directory: str | Path = ".") -> Dict[str, str]:
    """Return all pinned key→value pairs from the pins file."""
    return _load_pins_file(_pins_path(directory))


def save_pin(key: str, value: str, directory: str | Path = ".") -> None:
    """Persist a pin for *key* → *value*."""
    path = _pins_path(directory)
    pins = _load_pins_file(path)
    pins[key] = value
    _save_pins_file(path, pins)


def remove_pin(key: str, directory: str | Path = ".") -> bool:
    """Remove the pin for *key*.  Returns True if a pin existed."""
    path = _pins_path(directory)
    pins = _load_pins_file(path)
    if key not in pins:
        return False
    del pins[key]
    _save_pins_file(path, pins)
    return True


def check_pins(env: Dict[str, str], pins: Dict[str, str]) -> PinResult:
    """Check *env* against *pins* and return a ``PinResult``."""
    violations: List[PinViolation] = []
    for key, expected in pins.items():
        actual = env.get(key)
        if actual != expected:
            violations.append(PinViolation(key=key, expected=expected, actual=actual))
    return PinResult(violations=violations)
