"""Sorting utilities for environment variable diff output."""

from __future__ import annotations

from enum import Enum
from typing import List

from envoy_diff.differ import DiffResult


class SortOrder(str, Enum):
    KEY = "key"
    STATUS = "status"
    NONE = "none"


# Priority for status-based sorting: changed first, then added, removed, unchanged
_STATUS_PRIORITY = {
    "changed": 0,
    "added": 1,
    "removed": 2,
    "unchanged": 3,
}


def sort_diff_result(result: DiffResult, order: SortOrder = SortOrder.KEY) -> DiffResult:
    """Return a new DiffResult with keys sorted according to *order*.

    Args:
        result: The diff result to sort.
        order: One of SortOrder.KEY (alphabetical), SortOrder.STATUS
               (changed → added → removed → unchanged), or SortOrder.NONE
               (preserve insertion order).

    Returns:
        A new DiffResult with sorted key ordering.
    """
    if order is SortOrder.NONE:
        return result

    def _sort_key(item: tuple) -> tuple:
        key, entry = item
        if order is SortOrder.STATUS:
            status = entry.get("status", "unchanged")
            return (_STATUS_PRIORITY.get(status, 99), key.lower())
        # SortOrder.KEY
        return (key.lower(),)

    sorted_changed = dict(sorted(result["changed"].items(), key=_sort_key))
    sorted_added = dict(sorted(result["added"].items(), key=lambda i: i[0].lower()))
    sorted_removed = dict(sorted(result["removed"].items(), key=lambda i: i[0].lower()))
    sorted_unchanged = dict(sorted(result["unchanged"].items(), key=lambda i: i[0].lower()))

    return DiffResult(
        changed=sorted_changed,
        added=sorted_added,
        removed=sorted_removed,
        unchanged=sorted_unchanged,
    )


def sort_orders() -> List[str]:
    """Return all valid sort order names."""
    return [o.value for o in SortOrder]
