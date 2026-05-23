"""Tag environment variables with user-defined labels for grouping and annotation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

_DEFAULT_FILENAME = ".envoy_tags.json"


def _tags_path(directory: Optional[str] = None) -> Path:
    base = Path(directory) if directory else Path.cwd()
    return base / _DEFAULT_FILENAME


def _load_tags_file(path: Path) -> Dict[str, List[str]]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"Tags file must contain a JSON object, got {type(data).__name__}")
    return {k: list(v) for k, v in data.items()}


def _save_tags_file(path: Path, tags: Dict[str, List[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(tags, fh, indent=2, sort_keys=True)
        fh.write("\n")


def load_tags(directory: Optional[str] = None) -> Dict[str, List[str]]:
    """Return all key -> [tags] mappings from the tags file."""
    return _load_tags_file(_tags_path(directory))


def save_tag(key: str, tag: str, directory: Optional[str] = None) -> None:
    """Attach *tag* to *key*, creating the tags file if necessary."""
    path = _tags_path(directory)
    tags = _load_tags_file(path)
    existing = tags.get(key, [])
    if tag not in existing:
        existing.append(tag)
    tags[key] = existing
    _save_tags_file(path, tags)


def remove_tag(key: str, tag: str, directory: Optional[str] = None) -> None:
    """Remove *tag* from *key* if present; no-op if the tag does not exist."""
    path = _tags_path(directory)
    tags = _load_tags_file(path)
    if key in tags:
        tags[key] = [t for t in tags[key] if t != tag]
        if not tags[key]:
            del tags[key]
    _save_tags_file(path, tags)


def keys_for_tag(tag: str, directory: Optional[str] = None) -> List[str]:
    """Return all keys that carry the given *tag*."""
    tags = _load_tags_file(_tags_path(directory))
    return [k for k, ts in tags.items() if tag in ts]


def tags_for_key(key: str, directory: Optional[str] = None) -> List[str]:
    """Return the list of tags attached to *key*, or an empty list."""
    tags = _load_tags_file(_tags_path(directory))
    return tags.get(key, [])
