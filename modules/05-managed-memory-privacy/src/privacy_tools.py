"""Helpers for privacy-aware Memory administration.

These helpers are intentionally narrow:
- they operate on a single named Memory store,
- they only list scope identifiers / metadata, not message content,
- they only purge one explicitly named user identity at a time,
- and they include a log-redaction helper that is safe to unit test offline.
"""
from __future__ import annotations

import re
from typing import Any, Iterable


def _resolve_operation(target: Any, *names: str):
    for name in names:
        candidate = getattr(target, name, None)
        if callable(candidate):
            return candidate
    available = ", ".join(sorted(name for name in dir(target) if not name.startswith("_")))
    raise AttributeError(f"Target does not expose a supported memory operation. Available attributes: {available}")


def _extract_scope_name(item: Any) -> str:
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        for key in ("scope", "name", "id", "user_identity"):
            value = item.get(key)
            if isinstance(value, str) and value:
                return value
    for key in ("scope", "name", "id", "user_identity"):
        value = getattr(item, key, None)
        if isinstance(value, str) and value:
            return value
    return ""


def list_memory_scopes(memory_admin_client: Any, memory_store_name: str) -> list[str]:
    """List the identities or scope keys present for one Memory store.

    This helper is deliberately privacy-preserving: it returns only scope identifiers or labels,
    not the contents of stored memories.
    """
    if not memory_store_name:
        raise ValueError("memory_store_name is required.")

    operation = _resolve_operation(
        memory_admin_client,
        "list_memory_scopes",
        "list_scopes",
        "get_memory_scopes",
    )
    scopes: Iterable[Any] = operation(memory_store_name)
    results: list[str] = []
    for item in scopes:
        scope_name = _extract_scope_name(item)
        if scope_name:
            results.append(scope_name)
    return results


def purge_user_memory(user_identity: str, memory_admin_client: Any, memory_store_name: str) -> None:
    """Delete Memory only for the specified identity within one store.

    The operation never performs bulk deletion across all users. Callers must pass the exact target
    identity or scope to satisfy privacy / right-to-erasure workflows safely.
    """
    if not user_identity:
        raise ValueError("user_identity is required.")
    if not memory_store_name:
        raise ValueError("memory_store_name is required.")

    operation = _resolve_operation(
        memory_admin_client,
        "purge_user_memory",
        "purge_scope",
        "delete_scope",
        "delete_user_memory",
    )
    operation(memory_store_name, user_identity)


def redact_for_log(preference_text: str) -> str:
    """Return a short, sanitized log preview for a memory preference string."""
    text = (preference_text or "").strip()
    if not text:
        return "<empty>"

    collapsed = re.sub(r"\s+", " ", text)
    masked = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "[redacted-email]", collapsed)
    masked = re.sub(r"\d", "X", masked)

    limit = 48
    if len(masked) <= limit:
        return masked
    return masked[: limit - 3].rstrip() + "..."
