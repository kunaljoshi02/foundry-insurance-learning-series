"""Create, verify, or remove the module's isolated OBO toolbox assets.

This helper intentionally keeps the OBO path separate from shared managed-identity tooling:

- a remote-tool connection that forwards the caller's delegated user token
- a dedicated toolbox that references only that connection

The script is idempotent by design:

- the connection is upserted by name
- the toolbox version is derived from the desired YAML content hash
- cleanup deletes only the named module assets
"""
from __future__ import annotations

import argparse
import hashlib
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

try:  # pragma: no cover - depends on author environment
    from azure.identity import DefaultAzureCredential
except ImportError:  # pragma: no cover - depends on author environment
    DefaultAzureCredential = None  # type: ignore[assignment]

try:  # pragma: no cover - depends on author environment
    from azure.ai.projects import AIProjectClient
except ImportError:  # pragma: no cover - depends on author environment
    AIProjectClient = None  # type: ignore[assignment]


MODULE_NAME = "06-identity-rbac-auth-obo"
COURSE_NAME = "foundry-insurance-learning-series"
AI_SCOPE = "https://ai.azure.com/.default"
FEATURES_HEADER = "Toolbox=V1Preview"


class FoundryApiError(RuntimeError):
    """Raised when a Foundry project REST operation fails."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage the module's isolated OBO toolbox assets.")
    parser.add_argument("--config", required=True, help="Path to config.json")
    parser.add_argument(
        "--action",
        choices=("ensure", "verify", "cleanup"),
        default="ensure",
        help="Operation to perform.",
    )
    parser.add_argument("--what-if", action="store_true", help="Preview actions without making changes.")
    return parser.parse_args()


def build_project_client(endpoint: str, credential: Any) -> Any | None:
    """Best-effort SDK construction for environments where the package is installed."""

    if AIProjectClient is None:
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


def toolbox_yaml(connection_name: str) -> str:
    return (
        "description: isolated user-delegated toolbox for underwriting authority checks\n"
        "connections:\n"
        f"  - name: {connection_name}\n"
    )


def toolbox_version(connection_name: str) -> str:
    content = toolbox_yaml(connection_name).encode("utf-8")
    return f"v-{hashlib.sha1(content).hexdigest()[:10]}"


def multipart_bytes(file_name: str, content: str) -> tuple[bytes, str]:
    boundary = f"----foundry-{hashlib.sha1(content.encode('utf-8')).hexdigest()[:16]}"
    header = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="{file_name}"; filename="{file_name}"\r\n'
        "Content-Type: text/yaml\r\n\r\n"
    ).encode("utf-8")
    trailer = f"\r\n--{boundary}--\r\n".encode("utf-8")
    body = header + content.encode("utf-8") + trailer
    return body, f"multipart/form-data; boundary={boundary}"


class OboToolboxClient:
    def __init__(self, endpoint: str) -> None:
        if DefaultAzureCredential is None:  # pragma: no cover - depends on local environment
            raise RuntimeError(
                "Missing required packages. Install them with: "
                'pip install "azure-ai-projects>=2.3.0" azure-identity'
            )

        self.endpoint = endpoint.rstrip("/")
        self.credential = DefaultAzureCredential(exclude_interactive_browser_credential=False)
        self.project_client = build_project_client(self.endpoint, self.credential)

    @staticmethod
    def quote(value: str) -> str:
        return urllib.parse.quote(value, safe="")

    def token(self) -> str:
        return self.credential.get_token(AI_SCOPE).token

    def request(
        self,
        method: str,
        path: str,
        *,
        json_body: dict[str, Any] | list[Any] | None = None,
        raw_body: bytes | None = None,
        content_type: str = "application/json",
        expected: tuple[int, ...] = (200, 201, 202, 204),
    ) -> tuple[int, Any]:
        body = raw_body
        if json_body is not None:
            body = json.dumps(json_body).encode("utf-8")

        auth_header = "Bearer " + self.token()
        request = urllib.request.Request(
            self.endpoint + path,
            data=body,
            method=method,
            headers={
                "Authorization": auth_header,
                "Content-Type": content_type,
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
            error_body = exc.read().decode("utf-8", errors="replace")
            if exc.code in expected:
                return exc.code, error_body
            raise FoundryApiError(f"{method} {path} failed with HTTP {exc.code}: {error_body[:1200]}") from exc

    def get_connection(self, name: str) -> dict[str, Any] | None:
        code, payload = self.request(
            "GET",
            f"/connections/{self.quote(name)}?api-version=v1",
            expected=(200, 404),
        )
        return payload if code == 200 else None

    def upsert_connection(self, name: str, target: str, audience: str) -> dict[str, Any]:
        body = {
            "properties": {
                "category": "RemoteTool",
                "authType": "UserEntraToken",
                "target": target,
                "metadata": {
                    "type": "generic_mcp",
                    "audience": audience,
                    "course": COURSE_NAME,
                    "module": MODULE_NAME,
                },
            }
        }
        _, payload = self.request(
            "PUT",
            f"/connections/{self.quote(name)}?api-version=v1",
            json_body=body,
        )
        return payload

    def delete_connection(self, name: str) -> None:
        self.request(
            "DELETE",
            f"/connections/{self.quote(name)}?api-version=v1",
            expected=(200, 202, 204, 404),
        )

    def get_toolbox(self, name: str) -> dict[str, Any] | None:
        code, payload = self.request(
            "GET",
            f"/toolboxes/{self.quote(name)}?api-version=v1",
            expected=(200, 404),
        )
        return payload if code == 200 else None

    def list_toolbox_versions(self, name: str) -> list[dict[str, Any]]:
        code, payload = self.request(
            "GET",
            f"/toolboxes/{self.quote(name)}/versions?api-version=v1",
            expected=(200, 404),
        )
        if code == 404:
            return []
        return payload.get("value", payload if isinstance(payload, list) else [])

    def create_toolbox_version(self, name: str, version: str, yaml_text: str) -> dict[str, Any]:
        body, content_type = multipart_bytes("obo-toolbox.yaml", yaml_text)
        _, payload = self.request(
            "PUT",
            f"/toolboxes/{self.quote(name)}/versions/{self.quote(version)}?api-version=v1",
            raw_body=body,
            content_type=content_type,
        )
        return payload

    def set_default_toolbox_version(self, name: str, version: str) -> None:
        self.request(
            "POST",
            f"/toolboxes/{self.quote(name)}?api-version=v1",
            json_body={"default_version": version},
        )

    def delete_toolbox(self, name: str) -> None:
        self.request(
            "DELETE",
            f"/toolboxes/{self.quote(name)}?api-version=v1",
            expected=(200, 202, 204, 404),
        )


def module_metadata(payload: dict[str, Any] | None) -> dict[str, Any]:
    if not payload:
        return {}

    if isinstance(payload.get("properties"), dict):
        metadata = payload["properties"].get("metadata")
        if isinstance(metadata, dict):
            return metadata

    metadata = payload.get("metadata")
    return metadata if isinstance(metadata, dict) else {}


def assert_module_owned(payload: dict[str, Any] | None, resource_name: str) -> None:
    metadata = module_metadata(payload)
    module_name = metadata.get("module")
    if module_name and module_name != MODULE_NAME:
        raise FoundryApiError(
            f"Refusing to remove '{resource_name}' because it is tagged for module '{module_name}', not '{MODULE_NAME}'."
        )


def required_keys_for(action: str) -> list[str]:
    keys = ["foundryEndpoint", "oboToolboxName", "oboConnectionName"]
    if action == "ensure":
        keys.extend(["oboConnectionEndpoint", "oboConnectionAudience"])
    return keys


def ensure_assets(config: dict[str, Any], what_if: bool) -> int:
    desired_yaml = toolbox_yaml(str(config["oboConnectionName"]))
    desired_version = toolbox_version(str(config["oboConnectionName"]))

    if what_if:
        print(f"[WhatIf] Would upsert OBO connection '{config['oboConnectionName']}'.")
        print(f"[WhatIf] Would ensure toolbox '{config['oboToolboxName']}' has version '{desired_version}'.")
        return 0

    client = OboToolboxClient(str(config["foundryEndpoint"]))
    client.upsert_connection(
        str(config["oboConnectionName"]),
        str(config["oboConnectionEndpoint"]),
        str(config["oboConnectionAudience"]),
    )
    print(f"Upserted OBO connection '{config['oboConnectionName']}'.")

    existing_versions = client.list_toolbox_versions(str(config["oboToolboxName"]))
    version_exists = any(str(item.get("version")) == desired_version for item in existing_versions)
    if version_exists:
        print(f"Toolbox '{config['oboToolboxName']}' already has version '{desired_version}'; skipping upload.")
    else:
        client.create_toolbox_version(str(config["oboToolboxName"]), desired_version, desired_yaml)
        print(f"Created toolbox '{config['oboToolboxName']}' version '{desired_version}'.")

    client.set_default_toolbox_version(str(config["oboToolboxName"]), desired_version)
    print(f"Set toolbox '{config['oboToolboxName']}' default version to '{desired_version}'.")
    return 0


def verify_assets(config: dict[str, Any]) -> int:
    client = OboToolboxClient(str(config["foundryEndpoint"]))

    connection = client.get_connection(str(config["oboConnectionName"]))
    if connection is None:
        print(f"Missing connection: {config['oboConnectionName']}")
        return 1

    toolbox = client.get_toolbox(str(config["oboToolboxName"]))
    if toolbox is None:
        print(f"Missing toolbox: {config['oboToolboxName']}")
        return 1

    print(f"Verified connection '{config['oboConnectionName']}' exists.")
    metadata = module_metadata(connection)
    if metadata:
        print("Connection metadata:")
        print(json.dumps(metadata, indent=2))

    print(f"Verified toolbox '{config['oboToolboxName']}' exists.")
    return 0


def cleanup_assets(config: dict[str, Any], what_if: bool) -> int:
    if what_if:
        print(f"[WhatIf] Would delete toolbox '{config['oboToolboxName']}'.")
        print(f"[WhatIf] Would delete connection '{config['oboConnectionName']}'.")
        return 0

    client = OboToolboxClient(str(config["foundryEndpoint"]))

    toolbox = client.get_toolbox(str(config["oboToolboxName"]))
    assert_module_owned(toolbox, str(config["oboToolboxName"]))
    client.delete_toolbox(str(config["oboToolboxName"]))
    print(f"Deleted toolbox '{config['oboToolboxName']}' if it existed.")

    connection = client.get_connection(str(config["oboConnectionName"]))
    assert_module_owned(connection, str(config["oboConnectionName"]))
    client.delete_connection(str(config["oboConnectionName"]))
    print(f"Deleted connection '{config['oboConnectionName']}' if it existed.")
    return 0


def main() -> int:
    args = parse_args()
    try:
        config = load_config(args.config, required_keys=required_keys_for(args.action))
    except ConfigError as exc:
        print(exc)
        return 1

    if args.action == "ensure":
        return ensure_assets(config, args.what_if)
    if args.action == "verify":
        return verify_assets(config)
    return cleanup_assets(config, args.what_if)


if __name__ == "__main__":
    raise SystemExit(main())
