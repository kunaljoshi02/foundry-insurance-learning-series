"""Shared secret/tenant-specific-value scanner used by tests/scan-secrets.ps1 and module tests.

Pure stdlib regex scan — intentionally conservative (prefers false positives over missed leaks).
Flags: GUID-looking tenant/subscription IDs outside of known placeholder contexts, Azure resource
endpoints (*.azure.com, *.windows.net, *.cognitiveservices.azure.com, etc.), common key/secret
patterns, and absolute Windows/Unix local paths outside of documentation examples.
"""
from __future__ import annotations

import re
from pathlib import Path

GUID_RE = re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")
ENDPOINT_RE = re.compile(
    r"https?://[a-zA-Z0-9.-]+\.(?:azure\.com|windows\.net|cognitiveservices\.azure\.com|"
    r"openai\.azure\.com|search\.windows\.net|azurewebsites\.net)[^\s\"'<>]*"
)
SECRET_KEY_RE = re.compile(r"(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*[\"']?[A-Za-z0-9+/=_\-]{16,}[\"']?")
WINDOWS_PATH_RE = re.compile(r"[A-Za-z]:\\\\?Users\\\\?[^\"'\s]+", re.IGNORECASE)

ALLOWLIST_SUBSTRINGS = (
    "example.com",
    "contoso.com",
    "00000000-0000-0000-0000-000000000000",
    "<",  # placeholder markers like <tenant-id>
)

# Public, Microsoft-documented built-in RBAC role-definition GUIDs. These are fixed, global
# constants (same for every Azure tenant) — not tenant/subscription-specific secrets.
# See: https://learn.microsoft.com/azure/role-based-access-control/built-in-roles
BUILTIN_ROLE_GUIDS = {
    "53ca6127-db72-4b80-b1b0-d745d6d5456d",  # Azure AI User
    "eadc314b-1a2d-4efa-be10-5d325db5065e",  # Azure AI Project Manager
    "1407120a-92aa-4202-b7e9-c0e197c71c8f",  # Search Index Data Reader
    "8ebe5a00-799e-43f5-93ac-243d3dce84a7",  # Search Index Data Contributor
    "7ca78c08-252a-4471-8644-bb5ff32d4ba0",  # Search Service Contributor
    "a97b65f3-24c7-4388-baec-2e87135dc908",  # Cognitive Services User
    "2a2b9908-6ea1-4ae2-8e65-a410df84e7d1",  # Storage Blob Data Reader
}

# Generic, global Azure control-plane hostnames with no tenant/resource-specific prefix.
# These identify a *service*, not a customer resource, so they are safe to publish.
GENERIC_GLOBAL_HOSTS = {
    "ai.azure.com",
    "management.azure.com",
    "login.microsoftonline.com",
    "graph.microsoft.com",
    "cognitiveservices.azure.com",
}


def _is_allowlisted(line: str) -> bool:
    return any(token in line for token in ALLOWLIST_SUBSTRINGS)


def _is_builtin_role_guid(match_text: str) -> bool:
    return match_text.lower() in BUILTIN_ROLE_GUIDS


def _is_generic_global_endpoint(match_text: str) -> bool:
    host_match = re.match(r"https?://([a-zA-Z0-9.-]+)", match_text)
    if not host_match:
        return False
    return host_match.group(1).lower() in GENERIC_GLOBAL_HOSTS


def scan_text(text: str, source: str = "<text>") -> list[str]:
    """Return a list of human-readable findings for one block of text."""
    findings: list[str] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        if _is_allowlisted(line):
            continue
        for pattern, label, is_safe in (
            (GUID_RE, "GUID-like value (possible tenant/subscription/object ID)", _is_builtin_role_guid),
            (ENDPOINT_RE, "Azure resource endpoint", _is_generic_global_endpoint),
            (SECRET_KEY_RE, "possible secret/key/token literal", None),
            (WINDOWS_PATH_RE, "local Windows user path", None),
        ):
            match = pattern.search(line)
            if match and not (is_safe and is_safe(match.group(0))):
                findings.append(f"{source}:{lineno}: {label}: {line.strip()[:120]}")
    return findings


def scan_file(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []
    return scan_text(text, source=str(path))


def scan_paths(paths: list[Path], skip_names: set[str] | None = None) -> list[str]:
    skip_names = skip_names or {".git", "__pycache__", ".venv", "node_modules"}
    findings: list[str] = []
    for root in paths:
        if root.is_file():
            findings.extend(scan_file(root))
            continue
        for path in root.rglob("*"):
            if any(part in skip_names for part in path.parts):
                continue
            if path.is_file() and path.suffix.lower() in {
                ".md", ".json", ".yaml", ".yml", ".ps1", ".py", ".bicep", ".bicepparam", ".xml", ".txt",
            }:
                findings.extend(scan_file(path))
    return findings
