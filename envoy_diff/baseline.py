"""Baseline comparison: pin an env snapshot as the reference point for future diffs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

from envoy_diff.snapshotter import save_snapshot, load_snapshot

_BASELINE_FILENAME = ".envoy_baseline.json"


def baseline_path(directory: Optional[Path] = None) -> Path:
    """Return the default baseline file path within *directory* (cwd if None)."""
    base = directory if directory is not None else Path.cwd()
    return base / _BASELINE_FILENAME


def save_baseline(
    env: Dict[str, str],
    path: Optional[Path] = None,
    *,
    overwrite: bool = False,
) -> Path:
    """Persist *env* as the baseline at *path*.

    Delegates to :func:`save_snapshot` so the file format stays consistent.
    Set *overwrite* to ``True`` to replace an existing baseline.
    """
    dest = path if path is not None else baseline_path()
    if dest.exists() and not overwrite:
        raise FileExistsError(
            f"Baseline already exists at {dest}. Pass overwrite=True to replace it."
        )
    return save_snapshot(env, dest, overwrite=overwrite)


def load_baseline(path: Optional[Path] = None) -> Dict[str, str]:
    """Load the baseline env dict from *path* (default location if None)."""
    src = path if path is not None else baseline_path()
    if not src.exists():
        raise FileNotFoundError(f"No baseline found at {src}. Run 'save_baseline' first.")
    return load_snapshot(src)


def baseline_exists(path: Optional[Path] = None) -> bool:
    """Return ``True`` when a baseline file is present at *path*."""
    src = path if path is not None else baseline_path()
    return src.exists()


def clear_baseline(path: Optional[Path] = None) -> bool:
    """Delete the baseline file. Returns ``True`` if the file was removed."""
    src = path if path is not None else baseline_path()
    if src.exists():
        src.unlink()
        return True
    return False
