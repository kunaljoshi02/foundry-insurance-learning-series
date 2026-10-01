from __future__ import annotations

import argparse
import sys
from pathlib import Path

MODULE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = MODULE_ROOT.parents[1]
sys.path.insert(0, str(REPO_ROOT / "shared" / "python"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config_loader import ConfigError, load_config  # type: ignore  # noqa: E402
from foundry_toolbox_client import FoundryToolboxClient  # type: ignore  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create or update module Skills and toolbox.")
    parser.add_argument("--config", required=True, help="Path to config.json")
    parser.add_argument("--what-if", action="store_true", help="Show planned actions only")
    return parser.parse_args()


def skill_path(skill_name: str) -> Path:
    return MODULE_ROOT / "src" / "skills" / skill_name / "SKILL.md"


def main() -> int:
    args = parse_args()
    try:
        config = load_config(
            args.config,
            required_keys=[
                "foundryEndpoint",
                "chatModelDeploymentName",
                "agentName",
                "toolboxName",
                "toolboxVersion",
                "skills",
            ],
        )
    except ConfigError as exc:
        print(exc)
        return 1

    toolbox_path = MODULE_ROOT / "src" / "toolbox.yaml"
    if not toolbox_path.exists():
        print(f"Toolbox definition not found: {toolbox_path}")
        return 1

    skills = config["skills"]
    if args.what_if:
        print("[WhatIf] Would validate and provision the following Skills:")
        for skill in skills:
            print(f"  - {skill['name']} v{skill['version']} from {skill_path(skill['name']).relative_to(MODULE_ROOT)}")
        print(f"[WhatIf] Would provision toolbox '{config['toolboxName']}' v{config['toolboxVersion']} from src\\toolbox.yaml")
        return 0

    client = FoundryToolboxClient(config["foundryEndpoint"])

    for skill in skills:
        name = skill["name"]
        version = skill["version"]
        path = skill_path(name)
        if not path.exists():
            print(f"Missing Skill file: {path}")
            return 1

        existing_versions = client.list_skill_versions(name)
        version_exists = any(str(item.get("version")) == str(version) for item in existing_versions)
        if version_exists:
            print(f"Skill '{name}' already has version {version}; skipping upload.")
        else:
            client.create_skill_version(name, version, path)
            print(f"Created Skill '{name}' version {version}.")

        client.set_default_skill_version(name, version)
        print(f"Set Skill '{name}' default version to {version}.")

    toolbox_name = config["toolboxName"]
    toolbox_version = config["toolboxVersion"]
    existing_toolbox_versions = client.list_toolbox_versions(toolbox_name)
    toolbox_exists = any(str(item.get("version")) == str(toolbox_version) for item in existing_toolbox_versions)
    if toolbox_exists:
        print(f"Toolbox '{toolbox_name}' already has version {toolbox_version}; skipping upload.")
    else:
        client.create_toolbox_version(toolbox_name, toolbox_version, toolbox_path)
        print(f"Created toolbox '{toolbox_name}' version {toolbox_version}.")

    client.set_default_toolbox_version(toolbox_name, toolbox_version)
    print(f"Set toolbox '{toolbox_name}' default version to {toolbox_version}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
