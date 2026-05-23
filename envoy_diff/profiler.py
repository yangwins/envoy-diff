"""Profile support: named environment profiles stored in a config file."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List, Optional

DEFAULT_PROFILE_PATH = Path.home() / ".envoy_diff" / "profiles.json"


def _load_profiles_file(path: Path) -> Dict[str, dict]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"Profiles file must contain a JSON object, got {type(data).__name__}")
    return data


def _save_profiles_file(path: Path, data: Dict[str, dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
        fh.write("\n")


def list_profiles(path: Path = DEFAULT_PROFILE_PATH) -> List[str]:
    """Return the names of all stored profiles."""
    return sorted(_load_profiles_file(path).keys())


def save_profile(name: str, env: Dict[str, str], path: Path = DEFAULT_PROFILE_PATH) -> None:
    """Persist *env* under *name* in the profiles file."""
    if not name or not name.strip():
        raise ValueError("Profile name must not be empty")
    data = _load_profiles_file(path)
    data[name] = {str(k): str(v) for k, v in env.items()}
    _save_profiles_file(path, data)


def load_profile(name: str, path: Path = DEFAULT_PROFILE_PATH) -> Dict[str, str]:
    """Load a previously saved profile by *name*."""
    data = _load_profiles_file(path)
    if name not in data:
        raise KeyError(f"Profile {name!r} not found")
    return dict(data[name])


def delete_profile(name: str, path: Path = DEFAULT_PROFILE_PATH) -> bool:
    """Remove *name* from the profiles file.  Returns True if it existed."""
    data = _load_profiles_file(path)
    if name not in data:
        return False
    del data[name]
    _save_profiles_file(path, data)
    return True
