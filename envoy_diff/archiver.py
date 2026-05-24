"""Archive and retrieve named diff snapshots for historical comparison."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, List, Optional

_ARCHIVE_FILENAME = ".envoy_archive.json"


def _archive_path(directory: Optional[str] = None) -> Path:
    base = Path(directory) if directory else Path.cwd()
    return base / _ARCHIVE_FILENAME


def _load_archive_file(path: Path) -> Dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _save_archive_file(path: Path, data: Dict) -> None:
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
        fh.write("\n")


def list_archives(directory: Optional[str] = None) -> List[str]:
    """Return sorted list of archive names stored in *directory*."""
    path = _archive_path(directory)
    data = _load_archive_file(path)
    return sorted(data.keys())


def save_archive(
    name: str,
    env: Dict[str, str],
    directory: Optional[str] = None,
    overwrite: bool = False,
) -> Path:
    """Persist *env* under *name* in the archive file.

    Raises ``KeyError`` if *name* already exists and *overwrite* is False.
    """
    path = _archive_path(directory)
    data = _load_archive_file(path)
    if name in data and not overwrite:
        raise KeyError(f"Archive '{name}' already exists; use overwrite=True to replace.")
    data[name] = {
        "env": {str(k): str(v) for k, v in env.items()},
        "saved_at": time.time(),
    }
    _save_archive_file(path, data)
    return path.resolve()


def load_archive(name: str, directory: Optional[str] = None) -> Dict[str, str]:
    """Return the env dict stored under *name*.

    Raises ``KeyError`` if *name* is not found.
    """
    path = _archive_path(directory)
    data = _load_archive_file(path)
    if name not in data:
        raise KeyError(f"Archive '{name}' not found.")
    return dict(data[name]["env"])


def delete_archive(name: str, directory: Optional[str] = None) -> bool:
    """Remove *name* from the archive.  Returns True if it existed."""
    path = _archive_path(directory)
    data = _load_archive_file(path)
    if name not in data:
        return False
    del data[name]
    _save_archive_file(path, data)
    return True


def archive_metadata(name: str, directory: Optional[str] = None) -> Dict:
    """Return the full metadata record (env + saved_at) for *name*."""
    path = _archive_path(directory)
    data = _load_archive_file(path)
    if name not in data:
        raise KeyError(f"Archive '{name}' not found.")
    return dict(data[name])
