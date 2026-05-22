"""Loaders for reading environment variable sets from various sources."""

import json
import os
from pathlib import Path
from typing import Dict


EnvMap = Dict[str, str]


def load_from_env() -> EnvMap:
    """Load environment variables from the current process environment."""
    return dict(os.environ)


def load_from_file(path: str | Path) -> EnvMap:
    """Load environment variables from a file.

    Supports two formats:
      - .json: a flat JSON object mapping variable names to values
      - .env / plain text: KEY=VALUE lines (comments and blank lines ignored)
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Env file not found: {path}")

    if path.suffix == ".json":
        return _load_json(path)
    return _load_dotenv(path)


def load_from_dict(data: dict) -> EnvMap:
    """Load environment variables from a plain dictionary.

    All keys and values are coerced to strings.
    """
    if not isinstance(data, dict):
        raise TypeError(f"Expected a dict, got {type(data).__name__}")
    return {str(k): str(v) for k, v in data.items()}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _load_json(path: Path) -> EnvMap:
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"JSON file must contain a top-level object: {path}")
    return {str(k): str(v) for k, v in data.items()}


def _load_dotenv(path: Path) -> EnvMap:
    env: EnvMap = {}
    with path.open(encoding="utf-8") as fh:
        for lineno, raw_line in enumerate(fh, start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                raise ValueError(
                    f"Invalid line {lineno} in {path!r}: {raw_line!r}"
                )
            key, _, value = line.partition("=")
            # Strip optional surrounding quotes from value
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]
            env[key.strip()] = value
    return env
