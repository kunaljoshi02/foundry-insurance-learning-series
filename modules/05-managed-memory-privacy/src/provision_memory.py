"""Create, verify, or clean up a managed Memory store for Module 05.

This script is intentionally conservative:
- loads config through the shared loader,
- creates the Memory store only if it doesn't exist,
- creates a new prompt-agent version only when Memory attachment changes,
- verifies configuration without reading user memory contents,
- and optionally purges one specified user's memory before teardown.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


MODULE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = MODULE_ROOT.parents[1]
SHARED_PYTHON = REPO_ROOT / "shared" / "python"
if str(SHARED_PYTHON) not in sys.path:
    sys.path.insert(0, str(SHARED_PYTHON))

SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from config_loader import ConfigError, load_config  # type: ignore  # noqa: E402
from privacy_tools import list_memory_scopes, purge_user_memory  # type: ignore  # noqa: E402


MEMORY_API_VERSION = "2025-11-15-preview"
AGENT_API_VERSION = "v1"
AI_SCOPE = "https://ai.azure.com/.default"
FEATURES_HEADER = "MemoryStores=V1Preview"


class FoundryApiError(RuntimeError):
    """Raised when a Foundry REST request fails."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage Module 05 Memory assets.")
    parser.add_argument("--action", choices=("ensure", "verify", "cleanup"), required=True)
    parser.add_argument("--config", required=True, help="Path to config.json")
    parser.add_argument("--what-if", action="store_true", help="Preview changes only")
    parser.add_argument("--purge-user-data", action="store_true", help="Purge a specific user scope before cleanup")
    parser.add_argument("--user-identity", help="Exact target identity or scope for targeted Memory purge")
    return parser.parse_args()


def fail(message: str, exit_code: int = 1) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return exit_code


def quote(value: str) -> str:
    return urllib.parse.quote(value, safe="")


def coerce_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if hasattr(value, "items"):
        try:
            return dict(value.items())
        except Exception:
            return {}
    return {}


def get_value(obj: Any, key: str, default: Any = None) -> Any:
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    if hasattr(obj, key):
        return getattr(obj, key)
    if hasattr(obj, "get"):
        try:
            return obj.get(key, default)
        except Exception:
            return default
    return default


def make_credential():
    try:
        from azure.identity import DefaultAzureCredential
    except ImportError as exc:  # pragma: no cover - depends on local environment
        raise RuntimeError(
            'Missing required packages. Install them with: pip install "azure-ai-projects>=2.3.0" azure-identity'
        ) from exc

    return DefaultAzureCredential(exclude_interactive_browser_credential=False)


def build_project_client(endpoint: str, credential: Any) -> Any | None:
    """Create an AIProjectClient when the installed SDK exposes a compatible constructor.

    The preview Memory endpoints used by this module still go through direct REST calls, but the
    shared import pattern remains aligned with the rest of the curriculum's Foundry scripts.
    """
    try:
        from azure.ai.projects import AIProjectClient
    except ImportError:  # pragma: no cover - optional at authoring time
        return None

    for kwargs in (
        {"endpoint": endpoint, "credential": credential},
        {"project_endpoint": endpoint, "credential": credential},
    ):
        try:
            return AIProjectClient(**kwargs)
        except TypeError:
            continue
    return None


class FoundryMemoryManager:
    """Minimal REST wrapper for preview Memory operations used by this module."""

    def __init__(self, endpoint: str) -> None:
        self.endpoint = endpoint.rstrip("/")
        self.credential = make_credential()
        self.project_client = build_project_client(self.endpoint, self.credential)

    def _token(self) -> str:
        return self.credential.get_token(AI_SCOPE).token

    def request(
        self,
        method: str,
        path: str,
        *,
        json_body: dict[str, Any] | list[Any] | None = None,
        expected: tuple[int, ...] = (200, 201, 202, 204),
    ) -> tuple[int, Any]:
        body = json.dumps(json_body).encode("utf-8") if json_body is not None else None
        request = urllib.request.Request(
            self.endpoint + path,
            data=body,
            method=method,
            headers={
                "Authorization": f"Bearer {self._token()}",
                "Content-Type": "application/json",
                "Foundry-Features": FEATURES_HEADER,
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                payload = response.read()
                if not payload:
                    return response.status, {}
                text = payload.decode("utf-8")
                try:
                    return response.status, json.loads(text)
                except json.JSONDecodeError:
                    return response.status, text
        except urllib.error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            if exc.code in expected:
                return exc.code, details
            raise FoundryApiError(f"{method} {path} failed with HTTP {exc.code}: {details[:1200]}") from exc

    def list_agents(self) -> list[dict[str, Any]]:
        _, payload = self.request("GET", f"/agents?api-version={AGENT_API_VERSION}")
        return payload.get("value", payload if isinstance(payload, list) else [])

    def get_agent(self, agent_name: str) -> dict[str, Any] | None:
        for agent in self.list_agents():
            if agent.get("name") == agent_name:
                return agent
        return None

    def list_versions(self, agent_name: str) -> list[dict[str, Any]]:
        code, payload = self.request(
            "GET",
            f"/agents/{quote(agent_name)}/versions?api-version={AGENT_API_VERSION}",
            expected=(200, 404),
        )
        if code == 404:
            return []
        return payload.get("value", payload if isinstance(payload, list) else [])

    def latest_version(self, agent_name: str) -> dict[str, Any] | None:
        versions = self.list_versions(agent_name)
        if not versions:
            return None

        def sort_key(item: dict[str, Any]) -> tuple[str, str]:
            return (
                str(item.get("created_at") or item.get("createdAt") or ""),
                str(item.get("version") or ""),
            )

        return sorted(versions, key=sort_key)[-1]

    def create_agent_version(
        self,
        agent_name: str,
        definition: dict[str, Any],
        *,
        description: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"definition": definition}
        if description:
            payload["description"] = description
        if metadata:
            payload["metadata"] = metadata
        _, created = self.request(
            "POST",
            f"/agents/{quote(agent_name)}/versions?api-version={AGENT_API_VERSION}",
            json_body=payload,
        )
        return created

    def get_memory_store(self, store_name: str) -> dict[str, Any] | None:
        code, payload = self.request(
            "GET",
            f"/memory_stores/{quote(store_name)}?api-version={MEMORY_API_VERSION}",
            expected=(200, 404),
        )
        return payload if code == 200 else None

    def create_memory_store(self, payload: dict[str, Any]) -> dict[str, Any]:
        _, created = self.request(
            "POST",
            f"/memory_stores?api-version={MEMORY_API_VERSION}",
            json_body=payload,
        )
        return created

    def delete_memory_store(self, store_name: str) -> None:
        self.request(
            "DELETE",
            f"/memory_stores/{quote(store_name)}?api-version={MEMORY_API_VERSION}",
            expected=(200, 202, 204, 404),
        )

    def list_memory_scopes(self, store_name: str) -> list[dict[str, Any]]:
        code, payload = self.request(
            "GET",
            f"/memory_stores/{quote(store_name)}/memory_scopes?api-version={MEMORY_API_VERSION}",
            expected=(200, 404),
        )
        if code == 404:
            return []
        return payload.get("value", payload.get("data", payload if isinstance(payload, list) else []))

    def purge_scope(self, store_name: str, user_identity: str) -> None:
        self.request(
            "DELETE",
            f"/memory_stores/{quote(store_name)}/memory_scopes/{quote(user_identity)}?api-version={MEMORY_API_VERSION}",
            expected=(200, 202, 204, 404),
        )


def load_module_config(config_path: str) -> dict[str, Any]:
    return load_config(
        config_path,
        required_keys=[
            "foundryEndpoint",
            "agentName",
            "memoryStoreName",
        ],
    )


def desired_metadata(config: dict[str, Any]) -> dict[str, str]:
    metadata = {
        "course": "foundry-insurance-learning-series",
        "module": "05-managed-memory-privacy",
    }
    for key, value in coerce_dict(config.get("tags")).items():
        if isinstance(value, str) and value:
            metadata[key] = value
    return metadata


def desired_memory_tool(store_name: str, update_delay: int) -> dict[str, Any]:
    return {
        "type": "memory_search_preview",
        "memory_store_name": store_name,
        "scope": "{{$userId}}",
        "update_delay": update_delay,
    }


def tools_match(existing: dict[str, Any], desired: dict[str, Any]) -> bool:
    return (
        existing.get("type") == desired.get("type")
        and existing.get("memory_store_name") == desired.get("memory_store_name")
        and existing.get("scope") == desired.get("scope")
        and int(existing.get("update_delay", 0)) == int(desired.get("update_delay", 0))
    )


def with_attached_memory(definition: dict[str, Any], store_name: str, update_delay: int) -> tuple[dict[str, Any], bool]:
    updated = json.loads(json.dumps(definition))
    desired_tool = desired_memory_tool(store_name, update_delay)
    tools = list(updated.get("tools") or [])

    for tool in tools:
        if tools_match(tool, desired_tool):
            return updated, False

    replaced = False
    for index, tool in enumerate(tools):
        if tool.get("type") == "memory_search_preview" and tool.get("memory_store_name") == store_name:
            tools[index] = desired_tool
            replaced = True
            break

    if not replaced:
        tools.append(desired_tool)

    updated["tools"] = tools
    return updated, True


def without_attached_memory(definition: dict[str, Any], store_name: str) -> tuple[dict[str, Any], bool]:
    updated = json.loads(json.dumps(definition))
    tools = list(updated.get("tools") or [])
    kept = [tool for tool in tools if not (tool.get("type") == "memory_search_preview" and tool.get("memory_store_name") == store_name)]
    changed = len(kept) != len(tools)
    updated["tools"] = kept
    return updated, changed


def ensure_memory_store(manager: FoundryMemoryManager, config: dict[str, Any], agent_definition: dict[str, Any], what_if: bool) -> int:
    store_name = str(config["memoryStoreName"])
    agent_model = str(agent_definition.get("model") or "")
    if not agent_model:
        raise FoundryApiError("The target agent version does not expose a model name to reuse for the Memory store.")

    existing = manager.get_memory_store(store_name)
    if existing is not None:
        print(f"Memory store '{store_name}' already exists.")
        return 0

    if what_if:
        print(f"WhatIf: would create Memory store '{store_name}' using agent model '{agent_model}'.")
        return 0

    embedding_model = str(config.get("embeddingModelDeploymentName", "text-embedding-3-small"))
    payload = {
        "name": store_name,
        "description": (
            "Managed Memory for Module 05. Stores low-risk, synthetic per-user presentation "
            "preferences for the insurance advisor."
        ),
        "metadata": desired_metadata(config),
        "definition": {
            "kind": "default",
            "chat_model": agent_model,
            "embedding_model": embedding_model,
            "options": {
                "chat_summary_enabled": True,
                "user_profile_enabled": True,
                "procedural_memory_enabled": True,
                "default_ttl_seconds": 0,
                "user_profile_details": (
                    "Store only low-risk training preferences such as response structure, "
                    "currency-display preferences, and concise-summary instructions. Do not "
                    "store real customer PII, credentials, financial account data, claim-system "
                    "identifiers, medical details, or precise locations."
                ),
            },
        },
    }
    created = manager.create_memory_store(payload)
    print(f"Created Memory store '{created.get('name', store_name)}'.")
    return 0


def ensure_attachment(manager: FoundryMemoryManager, config: dict[str, Any], version: dict[str, Any], what_if: bool) -> int:
    agent_name = str(config["agentName"])
    store_name = str(config["memoryStoreName"])
    update_delay = int(config.get("memoryUpdateDelaySeconds", 1))

    definition = coerce_dict(version.get("definition"))
    updated_definition, changed = with_attached_memory(definition, store_name, update_delay)
    if not changed:
        print(f"Agent '{agent_name}' already has Memory store '{store_name}' attached.")
        return 0

    if what_if:
        print(f"WhatIf: would create a new agent version for '{agent_name}' with Memory store '{store_name}' attached.")
        return 0

    created = manager.create_agent_version(
        agent_name,
        updated_definition,
        description=str(version.get("description") or ""),
        metadata=coerce_dict(version.get("metadata")),
    )
    print(f"Created updated agent version '{created.get('version', '<unknown>')}' for '{agent_name}'.")
    return 0


def ensure(manager: FoundryMemoryManager, config: dict[str, Any], what_if: bool) -> int:
    agent_name = str(config["agentName"])
    agent = manager.get_agent(agent_name)
    if agent is None:
        return fail(f"Agent '{agent_name}' was not found. Create or import it before enabling Memory.")

    version = manager.latest_version(agent_name)
    if version is None:
        return fail(f"Agent '{agent_name}' has no versions to extend with Memory.")

    definition = coerce_dict(version.get("definition"))
    if definition.get("kind") != "prompt":
        print("Note: continuing even though the latest version did not explicitly report kind='prompt'.")

    ensure_memory_store(manager, config, definition, what_if)
    ensure_attachment(manager, config, version, what_if)
    return 0


def verify(manager: FoundryMemoryManager, config: dict[str, Any]) -> int:
    store_name = str(config["memoryStoreName"])
    agent_name = str(config["agentName"])

    store = manager.get_memory_store(store_name)
    if store is None:
        return fail(f"Expected Memory store '{store_name}' was not found.")

    version = manager.latest_version(agent_name)
    if version is None:
        return fail(f"Expected agent '{agent_name}' or its versions were not found.")

    definition = coerce_dict(version.get("definition"))
    tools = list(definition.get("tools") or [])
    attached = any(
        tool.get("type") == "memory_search_preview" and tool.get("memory_store_name") == store_name
        for tool in tools
    )
    if not attached:
        return fail(f"Agent '{agent_name}' is present, but Memory store '{store_name}' is not attached in the latest version.")

    print("Verified managed Memory configuration:")
    print(f"- agent: {agent_name}")
    print(f"- latest version: {version.get('version', '<unknown>')}")
    print(f"- memory store: {store_name}")
    print("- scope mode: {{$userId}}")
    print("- privacy check: verification intentionally does not read or dump any user memory contents")
    return 0


def cleanup(manager: FoundryMemoryManager, config: dict[str, Any], what_if: bool, purge_user_data: bool, user_identity: str | None) -> int:
    agent_name = str(config["agentName"])
    store_name = str(config["memoryStoreName"])
    version = manager.latest_version(agent_name)

    if version is None:
        print(f"Agent '{agent_name}' was not found or has no versions. Continuing with Memory store cleanup only.")
    else:
        updated_definition, changed = without_attached_memory(coerce_dict(version.get("definition")), store_name)
        if changed:
            if what_if:
                print(f"WhatIf: would create a new version of '{agent_name}' without Memory store '{store_name}'.")
            else:
                created = manager.create_agent_version(
                    agent_name,
                    updated_definition,
                    description=str(version.get("description") or ""),
                    metadata=coerce_dict(version.get("metadata")),
                )
                print(f"Created detached agent version '{created.get('version', '<unknown>')}' for '{agent_name}'.")
        else:
            print(f"Agent '{agent_name}' does not currently reference Memory store '{store_name}'.")

    if purge_user_data:
        if not user_identity:
            return fail("--purge-user-data requires --user-identity.")
        if what_if:
            print(f"WhatIf: would purge Memory only for identity '{user_identity}' in store '{store_name}'.")
        else:
            try:
                scopes = list_memory_scopes(manager, store_name)
                if scopes:
                    print(f"Visible Memory scopes before purge: {len(scopes)}")
            except Exception:
                print("Scope listing is unavailable in this environment; continuing with targeted purge request.")
            purge_user_memory(user_identity, manager, store_name)
            print(f"Requested targeted purge for identity '{user_identity}'.")

    store = manager.get_memory_store(store_name)
    if store is None:
        print(f"Memory store '{store_name}' does not exist. Nothing to delete.")
        return 0

    if what_if:
        print(f"WhatIf: would delete Memory store '{store_name}'.")
        return 0

    manager.delete_memory_store(store_name)
    print(f"Deleted Memory store '{store_name}'.")
    return 0


def main() -> int:
    args = parse_args()
    try:
        config = load_module_config(args.config)
    except ConfigError as exc:
        return fail(str(exc))

    try:
        manager = FoundryMemoryManager(str(config["foundryEndpoint"]))
        if args.action == "ensure":
            return ensure(manager, config, args.what_if)
        if args.action == "verify":
            return verify(manager, config)
        if args.action == "cleanup":
            return cleanup(
                manager,
                config,
                args.what_if,
                args.purge_user_data,
                args.user_identity,
            )
    except Exception as exc:  # pragma: no cover - runtime / network dependent
        return fail(str(exc))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
