"""Snapshot support: save and load environment snapshots to/from disk."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

ENV_DICT = Dict[str, str]


def _timestamp() -> str:
    """Return current UTC timestamp in ISO-8601 format."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def save_snapshot(
    env: ENV_DICT,
    path: str | Path,
    label: Optional[str] = None,
    *,
    overwrite: bool = False,
) -> Path:
    """Persist *env* as a JSON snapshot file.

    Parameters
    ----------
    env:       Flat ``{str: str}`` environment mapping.
    path:      Destination file path (must end in ``.json``).
    label:     Optional human-readable label stored in the snapshot metadata.
    overwrite: When *False* (default) raise ``FileExistsError`` if the file
               already exists.

    Returns the resolved ``Path`` of the written file.
    """
    dest = Path(path)
    if dest.suffix.lower() != ".json":
        raise ValueError(f"Snapshot path must end in .json, got: {path}")
    if dest.exists() and not overwrite:
        raise FileExistsError(f"Snapshot already exists: {dest}")

    dest.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "meta": {
            "created_at": _timestamp(),
            "label": label or "",
            "key_count": len(env),
        },
        "env": env,
    }
    dest.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return dest.resolve()


def load_snapshot(path: str | Path) -> ENV_DICT:
    """Load an environment mapping from a previously saved snapshot file.

    Raises
    ------
    FileNotFoundError  – if *path* does not exist.
    ValueError         – if the file is not a valid snapshot.
    """
    src = Path(path)
    if not src.exists():
        raise FileNotFoundError(f"Snapshot not found: {src}")

    try:
        payload = json.loads(src.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in snapshot {src}: {exc}") from exc

    if "env" not in payload or not isinstance(payload["env"], dict):
        raise ValueError(f"Snapshot {src} is missing a valid 'env' key.")

    return {str(k): str(v) for k, v in payload["env"].items()}


def snapshot_metadata(path: str | Path) -> dict:
    """Return only the ``meta`` block of a snapshot without loading all keys."""
    src = Path(path)
    if not src.exists():
        raise FileNotFoundError(f"Snapshot not found: {src}")
    payload = json.loads(src.read_text(encoding="utf-8"))
    return payload.get("meta", {})
