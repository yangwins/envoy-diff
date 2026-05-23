"""Audit log for environment diff operations."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

DEFAULT_AUDIT_FILE = ".envoy_audit.json"


@dataclass
class AuditEntry:
    timestamp: float
    operation: str
    source_a: str
    source_b: str
    added: int
    removed: int
    changed: int
    user: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "operation": self.operation,
            "source_a": self.source_a,
            "source_b": self.source_b,
            "added": self.added,
            "removed": self.removed,
            "changed": self.changed,
            "user": self.user,
            "tags": self.tags,
        }


def _audit_path(directory: Path) -> Path:
    return directory / DEFAULT_AUDIT_FILE


def record(
    operation: str,
    source_a: str,
    source_b: str,
    added: int,
    removed: int,
    changed: int,
    directory: Path = Path("."),
    user: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> AuditEntry:
    """Append an audit entry to the audit log and return it."""
    entry = AuditEntry(
        timestamp=time.time(),
        operation=operation,
        source_a=source_a,
        source_b=source_b,
        added=added,
        removed=removed,
        changed=changed,
        user=user,
        tags=tags or [],
    )
    path = _audit_path(directory)
    existing = load_audit(directory)
    existing.append(entry.as_dict())
    path.write_text(json.dumps(existing, indent=2))
    return entry


def load_audit(directory: Path = Path(".")) -> list:
    """Load all audit entries from the audit log file."""
    path = _audit_path(directory)
    if not path.exists():
        return []
    return json.loads(path.read_text())


def clear_audit(directory: Path = Path(".")) -> None:
    """Remove the audit log file if it exists."""
    path = _audit_path(directory)
    if path.exists():
        path.unlink()
