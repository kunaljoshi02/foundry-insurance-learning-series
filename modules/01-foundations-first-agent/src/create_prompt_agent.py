"""Create, verify, or delete the module's prompt agent.

This script is intentionally small and safe:
- loads local config.json through the shared loader,
- reads instructions from a local file,
- uses DefaultAzureCredential with the Foundry project endpoint,
- creates a new agent version only when the desired definition changed,
- verifies or deletes only the expected module-owned agent by name and metadata.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


MODULE_ROOT = Path(__file__).resolve().parent.parent
SHARED_PYTHON = MODULE_ROOT.parent.parent / "shared" / "python"
if str(SHARED_PYTHON) not in sys.path:
    sys.path.insert(0, str(SHARED_PYTHON))

from config_loader import ConfigError, load_config  # type: ignore  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage the Session 1 prompt agent.")
    parser.add_argument(
        "--action",
        choices=("ensure", "verify", "cleanup"),
        default="ensure",
        help="Operation to perform.",
    )
    parser.add_argument(
        "--config",
        default=str(MODULE_ROOT / "config.json"),
        help="Path to config.json.",
    )
    parser.add_argument(
        "--instructions-file",
        default=None,
        help="Optional override for the instructions file path.",
    )
    parser.add_argument(
        "--what-if",
        action="store_true",
        help="Preview actions without writing changes.",
    )
    return parser.parse_args()


def fail(message: str, exit_code: int = 1) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return exit_code


def as_dict(value: Any) -> dict[str, Any]:
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


def read_instructions(config: dict[str, Any], override: str | None) -> str:
    configured = override or config.get("agentInstructionsFile") or config.get("agentInstructions")
    if not configured:
        raise ConfigError("Config is missing 'agentInstructionsFile' or 'agentInstructions'.")

    candidate = Path(configured)
    if candidate.exists():
        return candidate.read_text(encoding="utf-8").strip()

    module_relative = (MODULE_ROOT / configured).resolve()
    if module_relative.exists():
        return module_relative.read_text(encoding="utf-8").strip()

    raise ConfigError(f"Instructions file not found: {configured}")


def load_module_inputs(config_path: str, instructions_override: str | None) -> tuple[dict[str, Any], str]:
    required_keys = ["foundryEndpoint", "chatModelDeploymentName", "agentName"]
    config = load_config(config_path, required_keys=required_keys)
    instructions = read_instructions(config, instructions_override)
    if not instructions:
        raise ConfigError("Agent instructions resolved to an empty file.")
    return config, instructions


def make_client(endpoint: str):
    try:
        from azure.identity import DefaultAzureCredential
        from azure.ai.projects import AIProjectClient
    except ImportError as exc:  # pragma: no cover - depends on local environment
        raise RuntimeError(
            "Missing required packages. Install them with: "
            'pip install "azure-ai-projects>=2.3.0" azure-identity'
        ) from exc

    return AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())


def desired_metadata(config: dict[str, Any]) -> dict[str, str]:
    metadata = {
        "course": "foundry-insurance-learning-series",
        "module": "01-foundations-first-agent",
    }
    tags = as_dict(config.get("tags"))
    for key, value in tags.items():
        if isinstance(value, str) and value:
            metadata[key] = value
    return metadata


def latest_version(project: Any, agent_name: str) -> Any | None:
    versions = list(project.agents.list_versions(agent_name=agent_name))
    if not versions:
        return None

    def sort_key(item: Any) -> str:
        return str(get_value(item, "version", ""))

    return sorted(versions, key=sort_key)[-1]


def definitions_match(version: Any, model_name: str, instructions: str, description: str | None, metadata: dict[str, str]) -> bool:
    if version is None:
        return False

    version_definition = get_value(version, "definition", {})
    existing_model = get_value(version_definition, "model", "")
    existing_instructions = get_value(version_definition, "instructions", "")
    existing_description = get_value(version, "description", "")
    existing_metadata = as_dict(get_value(version, "metadata", {}))

    metadata_matches = all(existing_metadata.get(key) == value for key, value in metadata.items())
    return (
        existing_model == model_name
        and existing_instructions == instructions
        and (existing_description or "") == (description or "")
        and metadata_matches
    )


def ensure_agent(project: Any, config: dict[str, Any], instructions: str, what_if: bool) -> int:
    from azure.core.exceptions import HttpResponseError
    from azure.ai.projects.models import PromptAgentDefinition

    agent_name = str(config["agentName"])
    description = str(config.get("agentDescription", "") or "")
    model_name = str(config["chatModelDeploymentName"])
    metadata = desired_metadata(config)

    try:
        agent = project.agents.get(agent_name=agent_name)
        print(f"Found existing agent endpoint: {get_value(agent, 'name', agent_name)}")
    except HttpResponseError as exc:
        if getattr(exc, "status_code", None) == 404:
            agent = None
            print(f"Agent '{agent_name}' does not exist yet.")
        else:
            raise

    version = None
    if agent is not None:
        version = latest_version(project, agent_name)

    if definitions_match(version, model_name, instructions, description, metadata):
        print(f"Agent '{agent_name}' is already up to date; no new version is required.")
        return 0

    if what_if:
        action = "create" if agent is None else "create a new version for"
        print(f"WhatIf: would {action} agent '{agent_name}' using model '{model_name}'.")
        return 0

    created = project.agents.create_version(
        agent_name=agent_name,
        definition=PromptAgentDefinition(
            model=model_name,
            instructions=instructions,
        ),
        description=description or None,
        metadata=metadata,
    )
    print(
        "Created agent version: "
        f"name={get_value(created, 'name', agent_name)} "
        f"version={get_value(created, 'version', '<unknown>')} "
        f"id={get_value(created, 'id', '<unknown>')}"
    )
    return 0


def verify_agent(project: Any, config: dict[str, Any]) -> int:
    agent_name = str(config["agentName"])
    found_agents = list(project.agents.list())
    names = [str(get_value(agent, "name", "")) for agent in found_agents]

    print("Agents in project:")
    for name in sorted(filter(None, names)):
        print(f"- {name}")

    if agent_name not in names:
        return fail(f"Expected agent '{agent_name}' was not found in the project.")

    version = latest_version(project, agent_name)
    print(
        f"Verified expected agent '{agent_name}' exists"
        + (
            f" (latest version: {get_value(version, 'version', '<unknown>')})."
            if version is not None
            else "."
        )
    )
    return 0


def cleanup_agent(project: Any, config: dict[str, Any], what_if: bool) -> int:
    from azure.core.exceptions import HttpResponseError

    agent_name = str(config["agentName"])
    expected_metadata = desired_metadata(config)

    try:
        agent = project.agents.get(agent_name=agent_name)
    except HttpResponseError as exc:
        if getattr(exc, "status_code", None) == 404:
            print(f"Agent '{agent_name}' does not exist. Nothing to delete.")
            return 0
        raise

    version = latest_version(project, agent_name)
    version_metadata = as_dict(get_value(version, "metadata", {}))
    if not all(version_metadata.get(key) == value for key, value in expected_metadata.items()):
        return fail(
            "Refusing to delete agent because its metadata does not match this module's ownership tags: "
            + json.dumps(version_metadata, sort_keys=True)
        )

    if what_if:
        print(f"WhatIf: would delete agent '{agent_name}'.")
        return 0

    project.agents.delete(agent_name=agent_name)
    print(f"Deleted agent '{get_value(agent, 'name', agent_name)}'.")
    return 0


def main() -> int:
    args = parse_args()
    try:
        config, instructions = load_module_inputs(args.config, args.instructions_file)
    except ConfigError as exc:
        return fail(str(exc))

    try:
        with make_client(str(config["foundryEndpoint"])) as project:
            if args.action == "ensure":
                return ensure_agent(project, config, instructions, args.what_if)
            if args.action == "verify":
                return verify_agent(project, config)
            if args.action == "cleanup":
                return cleanup_agent(project, config, args.what_if)
    except Exception as exc:  # pragma: no cover - network/runtime dependent
        return fail(str(exc))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
