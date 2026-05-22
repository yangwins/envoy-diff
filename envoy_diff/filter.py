"""Filter environment variable sets by key patterns."""

import fnmatch
import re
from typing import Dict, List, Optional


def filter_env(
    env: Dict[str, str],
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
    prefix: Optional[str] = None,
) -> Dict[str, str]:
    """Return a filtered copy of env based on include/exclude patterns and prefix.

    Args:
        env: The environment variable dict to filter.
        include: Glob patterns; only keys matching at least one are kept.
        exclude: Glob patterns; keys matching any are removed.
        prefix: If given, only keys starting with this prefix are kept.

    Returns:
        Filtered dict of environment variables.
    """
    result = dict(env)

    if prefix is not None:
        result = {k: v for k, v in result.items() if k.startswith(prefix)}

    if include:
        result = {
            k: v
            for k, v in result.items()
            if any(fnmatch.fnmatch(k, pat) for pat in include)
        }

    if exclude:
        result = {
            k: v
            for k, v in result.items()
            if not any(fnmatch.fnmatch(k, pat) for pat in exclude)
        }

    return result


def filter_keys_by_regex(
    env: Dict[str, str],
    pattern: str,
) -> Dict[str, str]:
    """Return only the entries whose keys match the given regex pattern.

    Args:
        env: The environment variable dict to filter.
        pattern: A regular expression string matched against each key.

    Returns:
        Filtered dict of environment variables.

    Raises:
        re.error: If the pattern is not a valid regular expression.
    """
    compiled = re.compile(pattern)
    return {k: v for k, v in env.items() if compiled.search(k)}
