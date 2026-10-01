"""Load and validate module configuration from config.json (copied from config.example.json).

Every module's scripts call `load_config()` so there is one consistent, tenant-agnostic way to
read local settings. Raises a clear error if config.json is missing or required keys are absent —
never falls back to hardcoded tenant-specific values.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


class ConfigError(RuntimeError):
    """Raised when module configuration is missing or invalid."""


def load_config(config_path: str | Path, required_keys: list[str] | None = None) -> dict[str, Any]:
    """Load a module's config.json and validate required keys are present and non-placeholder.

    Args:
        config_path: Path to the module's config.json (NOT config.example.json).
        required_keys: Top-level keys that must be present and not left as a placeholder
            (any string starting with '<' and ending with '>').

    Returns:
        The parsed configuration dict.

    Raises:
        ConfigError: if the file is missing, invalid JSON, or required keys are missing/placeholder.
    """
    path = Path(config_path)
    if not path.exists():
        example = path.with_name(path.stem + ".example" + path.suffix)
        hint = f" Copy {example.name} to {path.name} and fill in your own values." if example.exists() else ""
        raise ConfigError(f"Config file not found: {path}.{hint}")

    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Config file {path} is not valid JSON: {exc}") from exc

    for key in required_keys or []:
        value = config.get(key)
        if value is None:
            raise ConfigError(f"Config file {path} is missing required key '{key}'.")
        if isinstance(value, str) and value.startswith("<") and value.endswith(">"):
            raise ConfigError(
                f"Config file {path} still has a placeholder value for '{key}' ('{value}')."
                " Replace it with your own value."
            )

    return config


def env_or_config(key: str, config: dict[str, Any], default: Any = None) -> Any:
    """Prefer an environment variable override, then config.json, then a default."""
    return os.environ.get(key, config.get(key, default))
