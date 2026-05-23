"""Annotator: attach human-readable notes to diff keys."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

_DEFAULT_FILENAME = ".envoy_annotations.json"


def _annotations_path(directory: Optional[str] = None) -> Path:
    base = Path(directory) if directory else Path.cwd()
    return base / _DEFAULT_FILENAME


def _load_annotations_file(path: Path) -> Dict[str, str]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"Annotations file must contain a JSON object, got {type(data).__name__}")
    return {str(k): str(v) for k, v in data.items()}


def _save_annotations_file(path: Path, annotations: Dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(annotations, fh, indent=2, sort_keys=True)
        fh.write("\n")


def load_annotations(directory: Optional[str] = None) -> Dict[str, str]:
    """Return all stored annotations keyed by environment variable name."""
    return _load_annotations_file(_annotations_path(directory))


def save_annotation(key: str, note: str, directory: Optional[str] = None) -> Path:
    """Persist a note for *key*, overwriting any existing note."""
    path = _annotations_path(directory)
    annotations = _load_annotations_file(path)
    annotations[key] = note
    _save_annotations_file(path, annotations)
    return path.resolve()


def delete_annotation(key: str, directory: Optional[str] = None) -> bool:
    """Remove the annotation for *key*. Returns True if the key existed."""
    path = _annotations_path(directory)
    annotations = _load_annotations_file(path)
    if key not in annotations:
        return False
    del annotations[key]
    _save_annotations_file(path, annotations)
    return True


def annotate_diff(diff_keys: Dict[str, str], directory: Optional[str] = None) -> Dict[str, str]:
    """Return a mapping of diff key -> note for keys that have annotations.

    *diff_keys* is a dict whose keys are env-var names (values are ignored).
    """
    annotations = load_annotations(directory)
    return {k: annotations[k] for k in diff_keys if k in annotations}
