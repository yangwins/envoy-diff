"""Group diff result keys by a shared prefix or custom mapping."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envoy_diff.differ import DiffResult


@dataclass
class GroupedDiff:
    """Diff entries partitioned into named groups."""

    groups: Dict[str, List[str]] = field(default_factory=dict)
    ungrouped: List[str] = field(default_factory=list)

    def all_keys(self) -> List[str]:
        """Return every key that was assigned to any group."""
        result: List[str] = []
        for keys in self.groups.values():
            result.extend(keys)
        return result

    def as_dict(self) -> dict:
        return {
            "groups": {g: sorted(ks) for g, ks in self.groups.items()},
            "ungrouped": sorted(self.ungrouped),
        }


def group_by_prefix(
    result: DiffResult,
    prefixes: List[str],
    *,
    separator: str = "_",
    include_unchanged: bool = False,
) -> GroupedDiff:
    """Partition changed/added/removed keys into buckets by prefix.

    Args:
        result: The diff result to group.
        prefixes: Ordered list of prefixes to match (longest first wins).
        separator: Character that follows the prefix in a key name.
        include_unchanged: When True, unchanged keys are also grouped.

    Returns:
        A :class:`GroupedDiff` mapping each prefix to its matching keys.
    """
    prefixes_sorted = sorted(prefixes, key=len, reverse=True)

    candidate_keys: List[str] = (
        list(result.added)
        + list(result.removed)
        + list(result.changed)
    )
    if include_unchanged:
        candidate_keys += list(result.unchanged)

    groups: Dict[str, List[str]] = {p: [] for p in prefixes}
    ungrouped: List[str] = []

    for key in candidate_keys:
        matched: Optional[str] = None
        for prefix in prefixes_sorted:
            token = prefix + separator
            if key.upper().startswith(token.upper()):
                matched = prefix
                break
        if matched is not None:
            groups[matched].append(key)
        else:
            ungrouped.append(key)

    return GroupedDiff(groups=groups, ungrouped=ungrouped)


def group_by_mapping(
    result: DiffResult,
    mapping: Dict[str, List[str]],
    *,
    include_unchanged: bool = False,
) -> GroupedDiff:
    """Assign keys to groups according to an explicit key→group mapping.

    Args:
        result: The diff result to group.
        mapping: Dict of group_name → list of exact key names.
        include_unchanged: When True, unchanged keys are also considered.

    Returns:
        A :class:`GroupedDiff` with keys placed in declared groups.
    """
    candidate_keys: List[str] = (
        list(result.added)
        + list(result.removed)
        + list(result.changed)
    )
    if include_unchanged:
        candidate_keys += list(result.unchanged)

    key_to_group: Dict[str, str] = {}
    for group_name, keys in mapping.items():
        for k in keys:
            key_to_group[k] = group_name

    groups: Dict[str, List[str]] = {g: [] for g in mapping}
    ungrouped: List[str] = []

    for key in candidate_keys:
        group = key_to_group.get(key)
        if group is not None:
            groups[group].append(key)
        else:
            ungrouped.append(key)

    return GroupedDiff(groups=groups, ungrouped=ungrouped)
