"""aliaser.py – manage key aliases across environment variable sets.

Aliases allow a key in one environment to be treated as equivalent to a
differently-named key in another environment before diffing.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

_ALIASES_FILENAME = ".envoy_aliases.json"


def _aliases_path(directory: Optional[str] = None) -> Path:
    base = Path(directory) if directory else Path.cwd()
    return base / _ALIASES_FILENAME


def _load_aliases_file(path: Path) -> Dict[str, str]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise TypeError("Aliases file must contain a JSON object")
    return {str(k): str(v) for k, v in data.items()}


def _save_aliases_file(path: Path, aliases: Dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(aliases, fh, indent=2, sort_keys=True)
        fh.write("\n")


def load_aliases(directory: Optional[str] = None) -> Dict[str, str]:
    """Return the alias mapping stored on disk (empty dict if none)."""
    return _load_aliases_file(_aliases_path(directory))


def save_alias(from_key: str, to_key: str, directory: Optional[str] = None) -> Path:
    """Persist a single alias mapping *from_key* -> *to_key*."""
    path = _aliases_path(directory)
    aliases = _load_aliases_file(path)
    aliases[from_key] = to_key
    _save_aliases_file(path, aliases)
    return path


def remove_alias(from_key: str, directory: Optional[str] = None) -> bool:
    """Remove an alias.  Returns True if the key existed, False otherwise."""
    path = _aliases_path(directory)
    aliases = _load_aliases_file(path)
    if from_key not in aliases:
        return False
    del aliases[from_key]
    _save_aliases_file(path, aliases)
    return True


def apply_aliases(env: Dict[str, str], aliases: Dict[str, str]) -> Dict[str, str]:
    """Return a copy of *env* with keys renamed according to *aliases*.

    Keys not present in *aliases* are kept as-is.  If a rename would collide
    with an existing key the renamed key takes precedence.
    """
    if not isinstance(env, dict):
        raise TypeError("env must be a dict")
    result: Dict[str, str] = {}
    for key, value in env.items():
        new_key = aliases.get(key, key)
        result[new_key] = value
    return result


def list_aliases(directory: Optional[str] = None) -> List[str]:
    """Return a sorted list of registered alias source keys."""
    return sorted(load_aliases(directory).keys())
