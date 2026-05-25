"""Generate and apply patch objects that transform one env into another."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envoy_diff.differ import DiffResult, diff_envs


@dataclass
class PatchOperation:
    """A single operation within a patch."""

    op: str  # 'add' | 'remove' | 'replace'
    key: str
    value: Optional[str] = None
    old_value: Optional[str] = None

    def as_dict(self) -> Dict:
        d: Dict = {"op": self.op, "key": self.key}
        if self.value is not None:
            d["value"] = self.value
        if self.old_value is not None:
            d["old_value"] = self.old_value
        return d


@dataclass
class EnvPatch:
    """Ordered list of patch operations that transform *base* into *target*."""

    operations: List[PatchOperation] = field(default_factory=list)

    def is_empty(self) -> bool:
        return len(self.operations) == 0

    def as_dict(self) -> Dict:
        return {"operations": [op.as_dict() for op in self.operations]}


def build_patch(base: Dict[str, str], target: Dict[str, str]) -> EnvPatch:
    """Return an :class:`EnvPatch` that converts *base* into *target*."""
    result: DiffResult = diff_envs(base, target)
    ops: List[PatchOperation] = []

    for key, value in sorted(result.added.items()):
        ops.append(PatchOperation(op="add", key=key, value=value))

    for key, value in sorted(result.removed.items()):
        ops.append(PatchOperation(op="remove", key=key, old_value=value))

    for key, (old_val, new_val) in sorted(result.changed.items()):
        ops.append(PatchOperation(op="replace", key=key, value=new_val, old_value=old_val))

    return EnvPatch(operations=ops)


def apply_patch(base: Dict[str, str], patch: EnvPatch) -> Dict[str, str]:
    """Apply *patch* to *base* and return the resulting env dict.

    Raises ``ValueError`` if an operation cannot be applied cleanly.
    """
    env = dict(base)
    for op in patch.operations:
        if op.op == "add":
            if op.key in env:
                raise ValueError(f"Cannot add '{op.key}': key already exists.")
            env[op.key] = op.value  # type: ignore[assignment]
        elif op.op == "remove":
            if op.key not in env:
                raise ValueError(f"Cannot remove '{op.key}': key not found.")
            del env[op.key]
        elif op.op == "replace":
            if op.key not in env:
                raise ValueError(f"Cannot replace '{op.key}': key not found.")
            env[op.key] = op.value  # type: ignore[assignment]
        else:
            raise ValueError(f"Unknown patch operation: '{op.op}'")
    return env
