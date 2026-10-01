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

from config_loader import ConfigError, load_config  # type: ignore  # noqa: E402


ARM_API_VERSION = "2025-04-01-preview"
SEARCH_API_VERSION = "2025-02-01-preview"
MODULE_TAGS = {
    "course": "foundry-insurance-learning-series",
    "module": "03-search-grounding-foundry-iq",
}


class FoundryGroundingError(RuntimeError):
    """Raised when connection or agent grounding actions fail."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage the Module 03 Search connection and agent grounding.")
    parser.add_argument("--config", default=str(MODULE_ROOT / "config.json"), help="Path to config.json.")
    parser.add_argument(
        "--action",
        choices=("ensure", "verify", "detach"),
        default="ensure",
        help="Operation to perform.",
    )
    parser.add_argument("--delete-connection", action="store_true", help="Also delete the module Search connection.")
    parser.add_argument("--what-if", action="store_true", help="Preview changes without writing.")
    return parser.parse_args()


def fail(message: str, exit_code: int = 1) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return exit_code


def require_keys_for_action(action: str) -> list[str]:
    base = ["foundryEndpoint", "agentName", "searchConnectionName", "searchIndexName"]
    if action == "ensure":
        return base + ["searchServiceName", "resourceGroupName", "subscriptionId", "chatModelDeploymentName"]
    if action == "detach":
        return base + ["resourceGroupName", "subscriptionId"]
    return base


def build_project_client(endpoint: str) -> Any:
    try:
        from azure.ai.projects import AIProjectClient
        from azure.identity import DefaultAzureCredential
    except ImportError as exc:  # pragma: no cover - depends on author environment
        raise FoundryGroundingError(
            'Missing required packages. Install them with: pip install "azure-ai-projects>=2.0.0" azure-identity'
        ) from exc

    credential = DefaultAzureCredential(exclude_interactive_browser_credential=False)
    for kwargs in (
        {"endpoint": endpoint, "credential": credential},
        {"project_endpoint": endpoint, "credential": credential},
    ):
        try:
            return AIProjectClient(**kwargs)
        except TypeError:
            continue

    raise FoundryGroundingError("Unable to construct AIProjectClient with the installed SDK version.")


class ArmClient:
    def __init__(self) -> None:
        try:
            from azure.identity import DefaultAzureCredential
        except ImportError as exc:  # pragma: no cover - depends on author environment
            raise FoundryGroundingError(
                "Missing required packages. Install them with: pip install azure-identity"
            ) from exc

        self.credential = DefaultAzureCredential(exclude_interactive_browser_credential=False)

    def _token(self) -> str:
        return self.credential.get_token("https://management.azure.com/.default").token

    def request(
        self,
        method: str,
        url: str,
        *,
        body: dict[str, Any] | None = None,
        expected: tuple[int, ...] = (200, 201, 202, 204),
    ) -> tuple[int, Any]:
        request = urllib.request.Request(
            url,
            method=method,
            data=(json.dumps(body).encode("utf-8") if body is not None else None),
            headers={
                "Authorization": f"Bearer {self._token()}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                payload = response.read().decode("utf-8")
                if not payload:
                    return response.status, {}
                try:
                    return response.status, json.loads(payload)
                except json.JSONDecodeError:
                    return response.status, payload
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            if exc.code in expected:
                try:
                    return exc.code, json.loads(error_body)
                except json.JSONDecodeError:
                    return exc.code, error_body
            raise FoundryGroundingError(
                f"{method} {url} failed with HTTP {exc.code}: {error_body[:1200]}"
            ) from exc


def as_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if hasattr(value, "as_dict"):
        try:
            return value.as_dict()
        except Exception:
            return {}
    if hasattr(value, "items"):
        try:
            return dict(value.items())
        except Exception:
            return {}
    return {}


def get_value(value: Any, name: str, default: Any = None) -> Any:
    if value is None:
        return default
    if isinstance(value, dict):
        return value.get(name, default)
    if hasattr(value, name):
        return getattr(value, name)
    if hasattr(value, "get"):
        try:
            return value.get(name, default)
        except Exception:
            return default
    return default


def parse_foundry_endpoint(endpoint: str) -> dict[str, str]:
    cleaned = endpoint.rstrip("/")
    host = urllib.parse.urlparse(cleaned).netloc
    account_name = host.split(".", 1)[0]
    project_name = ""
    marker = "/api/projects/"
    if marker in cleaned:
        project_name = cleaned.split(marker, 1)[1].strip("/")

    return {
        "account_name": account_name,
        "project_name": project_name,
    }


def search_service_resource_id(config: dict[str, Any]) -> str:
    return (
        f"/subscriptions/{config['subscriptionId']}/resourceGroups/{config['resourceGroupName']}"
        f"/providers/Microsoft.Search/searchServices/{config['searchServiceName']}"
    )


def foundry_account_resource_id(config: dict[str, Any]) -> str:
    endpoint_bits = parse_foundry_endpoint(str(config["foundryEndpoint"]))
    account_name = str(config.get("foundryAccountName") or endpoint_bits["account_name"])
    return (
        f"/subscriptions/{config['subscriptionId']}/resourceGroups/{config['resourceGroupName']}"
        f"/providers/Microsoft.CognitiveServices/accounts/{account_name}"
    )


def foundry_connection_url(config: dict[str, Any]) -> str:
    return (
        "https://management.azure.com"
        f"{foundry_account_resource_id(config)}/connections/{config['searchConnectionName']}"
        f"?api-version={ARM_API_VERSION}"
    )


def get_search_service_details(config: dict[str, Any]) -> dict[str, Any]:
    arm = ArmClient()
    url = (
        "https://management.azure.com"
        f"{search_service_resource_id(config)}?api-version={SEARCH_API_VERSION}"
    )
    _status, payload = arm.request("GET", url)
    return payload


def ensure_connection(config: dict[str, Any], what_if: bool) -> None:
    if what_if:
        print(
            "WhatIf: would create or update Search connection "
            f"{config['searchConnectionName']!r} for service {config['searchServiceName']!r}."
        )
        return

    service = get_search_service_details(config)
    endpoint = get_value(service.get("properties", {}), "endpoint") or f"https://{config['searchServiceName']}.search.windows.net"
    location = get_value(service, "location", config.get("location", "<unknown>"))
    arm = ArmClient()
    body = {
        "properties": {
            "category": "CognitiveSearch",
            "target": endpoint,
            "authType": "AAD",
            "isSharedToAll": True,
            "metadata": {
                "ApiType": "Azure",
                "ResourceId": search_service_resource_id(config),
                "location": location,
                **MODULE_TAGS,
            },
        }
    }
    arm.request("PUT", foundry_connection_url(config), body=body)
    print(f"Ensured Foundry Search connection {config['searchConnectionName']!r}.")


def delete_connection(config: dict[str, Any], what_if: bool) -> None:
    if what_if:
        print(f"WhatIf: would delete Search connection {config['searchConnectionName']!r}.")
        return

    arm = ArmClient()
    _status, existing = arm.request("GET", foundry_connection_url(config), expected=(200, 404))
    if _status == 200:
        metadata = as_dict(get_value(existing.get("properties", {}), "metadata", {}))
        if metadata.get("course") != MODULE_TAGS["course"] or metadata.get("module") != MODULE_TAGS["module"]:
            raise FoundryGroundingError(
                f"Refusing to delete connection {config['searchConnectionName']!r}: ownership metadata does not match this module."
            )
    arm.request("DELETE", foundry_connection_url(config), expected=(200, 202, 204, 404))
    print(f"Deleted Search connection {config['searchConnectionName']!r} if it existed.")


def get_connection(project: Any, connection_name: str) -> Any:
    try:
        return project.connections.get(connection_name)
    except Exception as exc:
        raise FoundryGroundingError(
            f"Unable to resolve connection {connection_name!r} from the Foundry project. "
            "Make sure the connection exists and the installed SDK supports project.connections.get()."
        ) from exc


def build_search_tool(connection_id: str, index_name: str) -> Any:
    try:
        from azure.ai.projects.models import (
            AISearchIndexResource,
            AzureAISearchQueryType,
            AzureAISearchTool,
            AzureAISearchToolResource,
        )
    except ImportError as exc:  # pragma: no cover - depends on author environment
        raise FoundryGroundingError(
            'Missing required packages. Install them with: pip install "azure-ai-projects>=2.0.0"'
        ) from exc

    return AzureAISearchTool(
        azure_ai_search=AzureAISearchToolResource(
            indexes=[
                AISearchIndexResource(
                    project_connection_id=connection_id,
                    index_name=index_name,
                    query_type=AzureAISearchQueryType.VECTOR_SEMANTIC_HYBRID,
                )
            ]
        )
    )


def latest_agent_version(project: Any, agent_name: str) -> Any:
    versions = list(project.agents.list_versions(agent_name=agent_name))
    if not versions:
        raise FoundryGroundingError(f"Agent {agent_name!r} exists but has no versions to update.")
    versions.sort(key=lambda item: str(get_value(item, "version", "")))
    return versions[-1]


def extract_search_indexes(tool: Any) -> list[dict[str, Any]]:
    payload = as_dict(tool)
    candidate = payload.get("azure_ai_search") or payload.get("azureAiSearch") or payload
    candidate_dict = as_dict(candidate)
    indexes = candidate_dict.get("indexes", [])
    return [as_dict(index) for index in indexes if as_dict(index)]


def agent_has_search_tool(version: Any, connection_id: str, index_name: str) -> bool:
    definition = get_value(version, "definition", {})
    tools = list(get_value(definition, "tools", []) or [])
    for tool in tools:
        indexes = extract_search_indexes(tool)
        for index in indexes:
            found_connection_id = index.get("project_connection_id") or index.get("projectConnectionId")
            found_index_name = index.get("index_name") or index.get("indexName")
            if found_connection_id == connection_id and found_index_name == index_name:
                return True
    return False


def create_grounded_agent_version(project: Any, config: dict[str, Any], connection_id: str, what_if: bool) -> None:
    try:
        from azure.ai.projects.models import PromptAgentDefinition
    except ImportError as exc:  # pragma: no cover - depends on author environment
        raise FoundryGroundingError(
            'Missing required packages. Install them with: pip install "azure-ai-projects>=2.0.0"'
        ) from exc

    agent_name = str(config["agentName"])
    latest = latest_agent_version(project, agent_name)
    if agent_has_search_tool(latest, connection_id, str(config["searchIndexName"])):
        print(f"Agent {agent_name!r} already references Search index {config['searchIndexName']!r}.")
        return

    definition = get_value(latest, "definition", {})
    existing_tools = list(get_value(definition, "tools", []) or [])
    existing_tools.append(build_search_tool(connection_id, str(config["searchIndexName"])))

    if what_if:
        print(
            "WhatIf: would create a new agent version for "
            f"{agent_name!r} with Azure AI Search grounding attached."
        )
        return

    created = project.agents.create_version(
        agent_name=agent_name,
        definition=PromptAgentDefinition(
            model=str(get_value(definition, "model", config["chatModelDeploymentName"])),
            instructions=str(get_value(definition, "instructions", "")),
            tools=existing_tools,
        ),
        description=get_value(latest, "description", None),
        metadata={**as_dict(get_value(latest, "metadata", {})), **MODULE_TAGS},
    )
    print(
        "Created grounded agent version: "
        f"name={get_value(created, 'name', agent_name)} "
        f"version={get_value(created, 'version', '<unknown>')}"
    )


def detach_search_tool(project: Any, config: dict[str, Any], what_if: bool) -> None:
    try:
        from azure.ai.projects.models import PromptAgentDefinition
    except ImportError as exc:  # pragma: no cover - depends on author environment
        raise FoundryGroundingError(
            'Missing required packages. Install them with: pip install "azure-ai-projects>=2.0.0"'
        ) from exc

    agent_name = str(config["agentName"])
    latest = latest_agent_version(project, agent_name)
    definition = get_value(latest, "definition", {})
    tools = list(get_value(definition, "tools", []) or [])
    retained_tools = []
    removed = 0
    for tool in tools:
        indexes = extract_search_indexes(tool)
        if indexes and any(index.get("index_name") == config["searchIndexName"] for index in indexes):
            removed += 1
            continue
        retained_tools.append(tool)

    if removed == 0:
        print(f"Agent {agent_name!r} has no matching Search tool to detach.")
        return

    if what_if:
        print(f"WhatIf: would create a new version of {agent_name!r} without the Search grounding tool.")
        return

    created = project.agents.create_version(
        agent_name=agent_name,
        definition=PromptAgentDefinition(
            model=str(get_value(definition, "model", config.get("chatModelDeploymentName", ""))),
            instructions=str(get_value(definition, "instructions", "")),
            tools=retained_tools,
        ),
        description=get_value(latest, "description", None),
        metadata={**as_dict(get_value(latest, "metadata", {})), **MODULE_TAGS},
    )
    print(
        "Created detached agent version: "
        f"name={get_value(created, 'name', agent_name)} "
        f"version={get_value(created, 'version', '<unknown>')}"
    )


def verify_grounding(project: Any, config: dict[str, Any]) -> None:
    connection = get_connection(project, str(config["searchConnectionName"]))
    connection_id = str(get_value(connection, "id", ""))
    if not connection_id:
        raise FoundryGroundingError(
            f"Connection {config['searchConnectionName']!r} was found but did not expose an id."
        )

    latest = latest_agent_version(project, str(config["agentName"]))
    if not agent_has_search_tool(latest, connection_id, str(config["searchIndexName"])):
        raise FoundryGroundingError(
            f"Agent {config['agentName']!r} does not reference Search index {config['searchIndexName']!r}."
        )

    print(f"Verified connection {config['searchConnectionName']!r}: {connection_id}")
    print(f"Verified agent {config['agentName']!r} references Search index {config['searchIndexName']!r}.")


def main() -> int:
    args = parse_args()
    try:
        config = load_config(args.config, required_keys=require_keys_for_action(args.action))
    except ConfigError as exc:
        return fail(str(exc))

    try:
        project = build_project_client(str(config["foundryEndpoint"]))
        if args.action == "ensure":
            ensure_connection(config, args.what_if)
            if args.what_if:
                print("WhatIf: would resolve the connection and attach the Search tool to the agent.")
                return 0
            connection = get_connection(project, str(config["searchConnectionName"]))
            connection_id = str(get_value(connection, "id", ""))
            if not connection_id:
                raise FoundryGroundingError(
                    f"Connection {config['searchConnectionName']!r} was created but no connection id was returned."
                )
            create_grounded_agent_version(project, config, connection_id, args.what_if)
            return 0

        if args.action == "verify":
            verify_grounding(project, config)
            return 0

        if args.action == "detach":
            detach_search_tool(project, config, args.what_if)
            if args.delete_connection:
                delete_connection(config, args.what_if)
            return 0
    except FoundryGroundingError as exc:
        return fail(str(exc))
    except Exception as exc:  # pragma: no cover - defensive fallback for SDK/API drift
        return fail(f"Unexpected error: {exc}")

    return fail(f"Unsupported action: {args.action}")


if __name__ == "__main__":
    raise SystemExit(main())
