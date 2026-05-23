"""Ignorer: manage a persistent ignore-list of environment variable keys.

Keys on the ignore list are stripped from both sides before diffing,
so transient or intentionally-diverging variables don't create noise.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

_IGNORE_FILENAME = ".envoy_ignore.json"


def _ignore_path(directory: str | Path = ".") -> Path:
    return Path(directory) / _IGNORE_FILENAME


def _load_ignore_file(path: Path) -> List[str]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise ValueError(f"Ignore file {path} must contain a JSON array of strings.")
    return [str(k) for k in data]


def _save_ignore_file(path: Path, keys: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(sorted(set(keys)), fh, indent=2)
        fh.write("\n")


def load_ignored_keys(directory: str | Path = ".") -> List[str]:
    """Return the list of ignored keys from *directory*."""
    return _load_ignore_file(_ignore_path(directory))


def add_ignored_key(key: str, directory: str | Path = ".") -> List[str]:
    """Add *key* to the ignore list and persist it.  Returns the updated list."""
    path = _ignore_path(directory)
    keys = _load_ignore_file(path)
    if key not in keys:
        keys.append(key)
    _save_ignore_file(path, keys)
    return sorted(set(keys))


def remove_ignored_key(key: str, directory: str | Path = ".") -> List[str]:
    """Remove *key* from the ignore list.  Returns the updated list."""
    path = _ignore_path(directory)
    keys = _load_ignore_file(path)
    keys = [k for k in keys if k != key]
    _save_ignore_file(path, keys)
    return sorted(keys)


def apply_ignore(env: Dict[str, str], directory: str | Path = ".") -> Dict[str, str]:
    """Return a copy of *env* with all ignored keys removed."""
    ignored = set(load_ignored_keys(directory))
    return {k: v for k, v in env.items() if k not in ignored}


def clear_ignored_keys(directory: str | Path = ".") -> None:
    """Remove the ignore file entirely."""
    path = _ignore_path(directory)
    if path.exists():
        path.unlink()
