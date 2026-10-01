from __future__ import annotations

import json
import mimetypes
import uuid
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from azure.identity import DefaultAzureCredential

try:
    from azure.ai.projects import AIProjectClient
except ImportError:  # pragma: no cover - optional at authoring time
    AIProjectClient = None


AI_SCOPE = "https://ai.azure.com/.default"
FEATURES_HEADER = "Skills=V1Preview,Toolbox=V1Preview"


class FoundryApiError(RuntimeError):
    pass


def build_project_client(endpoint: str, credential: DefaultAzureCredential) -> Any | None:
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


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def multipart_file(path: Path) -> tuple[bytes, str]:
    boundary = f"----foundry-{uuid.uuid4().hex}"
    file_name = path.name
    mime_type = mimetypes.guess_type(file_name)[0] or "text/plain"
    content = path.read_bytes()
    header = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="{file_name}"; filename="{file_name}"\r\n'
        f"Content-Type: {mime_type}\r\n\r\n"
    ).encode("utf-8")
    trailer = f"\r\n--{boundary}--\r\n".encode("utf-8")
    return header + content + trailer, f"multipart/form-data; boundary={boundary}"


class FoundryToolboxClient:
    def __init__(self, endpoint: str) -> None:
        self.endpoint = endpoint.rstrip("/")
        self.credential = DefaultAzureCredential(exclude_interactive_browser_credential=False)
        self.project_client = build_project_client(self.endpoint, self.credential)

    def _token(self) -> str:
        return self.credential.get_token(AI_SCOPE).token

    def request(
        self,
        method: str,
        path: str,
        *,
        json_body: dict[str, Any] | list[Any] | None = None,
        raw_body: bytes | None = None,
        content_type: str = "application/json",
        expected: tuple[int, ...] = (200, 201, 204),
    ) -> tuple[int, Any]:
        body = raw_body
        if json_body is not None:
            body = json.dumps(json_body).encode("utf-8")

        request = urllib.request.Request(
            self.endpoint + path,
            data=body,
            method=method,
            headers={
                "Authorization": f"Bearer {self._token()}",
                "Content-Type": content_type,
                "Foundry-Features": FEATURES_HEADER,
            },
        )

        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                payload = response.read()
                if not payload:
                    return response.status, {}
                content = payload.decode("utf-8")
                try:
                    return response.status, json.loads(content)
                except json.JSONDecodeError:
                    return response.status, content
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            if exc.code in expected:
                return exc.code, error_body
            raise FoundryApiError(
                f"{method} {path} failed with HTTP {exc.code}: {error_body[:1200]}"
            ) from exc

    @staticmethod
    def quote(value: str) -> str:
        return urllib.parse.quote(value, safe="")

    def list_skills(self) -> list[dict[str, Any]]:
        _, payload = self.request("GET", "/skills?api-version=v1")
        return payload.get("value", payload if isinstance(payload, list) else [])

    def get_skill(self, name: str) -> dict[str, Any] | None:
        code, payload = self.request(
            "GET",
            f"/skills/{self.quote(name)}?api-version=v1",
            expected=(200, 404),
        )
        return payload if code == 200 else None

    def list_skill_versions(self, name: str) -> list[dict[str, Any]]:
        code, payload = self.request(
            "GET",
            f"/skills/{self.quote(name)}/versions?api-version=v1",
            expected=(200, 404),
        )
        if code == 404:
            return []
        return payload.get("value", payload if isinstance(payload, list) else [])

    def create_skill_version(self, name: str, version: str, skill_path: Path) -> dict[str, Any]:
        body, content_type = multipart_file(skill_path)
        _, payload = self.request(
            "PUT",
            f"/skills/{self.quote(name)}/versions/{self.quote(version)}?api-version=v1",
            raw_body=body,
            content_type=content_type,
        )
        return payload

    def set_default_skill_version(self, name: str, version: str) -> None:
        self.request(
            "POST",
            f"/skills/{self.quote(name)}?api-version=v1",
            json_body={"default_version": version},
        )

    def list_toolboxes(self) -> list[dict[str, Any]]:
        _, payload = self.request("GET", "/toolboxes?api-version=v1")
        return payload.get("value", payload if isinstance(payload, list) else [])

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

    def create_toolbox_version(self, name: str, version: str, toolbox_path: Path) -> dict[str, Any]:
        body, content_type = multipart_file(toolbox_path)
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

    def list_agents(self) -> list[dict[str, Any]]:
        _, payload = self.request("GET", "/agents?api-version=v1")
        return payload.get("value", payload if isinstance(payload, list) else [])

    def get_agent(self, agent_name: str) -> dict[str, Any] | None:
        for agent in self.list_agents():
            if agent.get("name") == agent_name:
                return agent
        return None

    def get_agent_toolboxes(self, agent_name: str) -> list[dict[str, Any]]:
        agent = self.get_agent(agent_name)
        if not agent:
            raise FoundryApiError(f"Agent '{agent_name}' was not found.")
        return agent.get("toolboxes", []) or agent.get("toolbox_references", [])

    def set_agent_toolboxes(self, agent_name: str, toolbox_names: list[str]) -> None:
        agent = self.get_agent(agent_name)
        if not agent:
            raise FoundryApiError(f"Agent '{agent_name}' was not found.")

        agent_id = agent.get("id", agent_name)
        payload = {"toolboxes": [{"name": name} for name in toolbox_names]}
        self.request(
            "PATCH",
            f"/agents/{self.quote(str(agent_id))}?api-version=v1",
            json_body=payload,
        )

    def delete_toolbox(self, name: str) -> None:
        self.request(
            "DELETE",
            f"/toolboxes/{self.quote(name)}?api-version=v1",
            expected=(200, 202, 204, 404),
        )

    def delete_skill(self, name: str) -> None:
        self.request(
            "DELETE",
            f"/skills/{self.quote(name)}?api-version=v1",
            expected=(200, 202, 204, 404),
        )
