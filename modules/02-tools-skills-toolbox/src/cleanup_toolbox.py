from __future__ import annotations

import argparse
import sys
from pathlib import Path

MODULE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = MODULE_ROOT.parents[1]
sys.path.insert(0, str(REPO_ROOT / "shared" / "python"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config_loader import ConfigError, load_config  # type: ignore  # noqa: E402
from foundry_toolbox_client import FoundryApiError, FoundryToolboxClient  # type: ignore  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Detach and delete module-created toolbox assets.")
    parser.add_argument("--config", required=True, help="Path to config.json")
    parser.add_argument("--detach-agent", action="store_true", help="Detach the toolbox from the configured agent first")
    parser.add_argument("--what-if", action="store_true", help="Show planned actions only")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        config = load_config(
            args.config,
            required_keys=["foundryEndpoint", "agentName", "toolboxName", "skills"],
        )
    except ConfigError as exc:
        print(exc)
        return 1

    if args.what_if:
        if args.detach_agent:
            print(f"[WhatIf] Would detach toolbox '{config['toolboxName']}' from agent '{config['agentName']}'.")
        print(f"[WhatIf] Would delete toolbox '{config['toolboxName']}'.")
        for skill in config["skills"]:
            print(f"[WhatIf] Would delete Skill '{skill['name']}'.")
        return 0

    client = FoundryToolboxClient(config["foundryEndpoint"])

    if args.detach_agent:
        try:
            current = client.get_agent_toolboxes(config["agentName"])
            remaining = sorted(
                {
                    item.get("name")
                    for item in current
                    if item.get("name") and item.get("name") != config["toolboxName"]
                }
            )
            client.set_agent_toolboxes(config["agentName"], remaining)
            print(f"Detached toolbox '{config['toolboxName']}' from agent '{config['agentName']}'.")
        except FoundryApiError as exc:
            print(f"Warning: could not detach toolbox from agent. {exc}")

    client.delete_toolbox(config["toolboxName"])
    print(f"Deleted toolbox '{config['toolboxName']}' if it existed.")

    for skill in config["skills"]:
        client.delete_skill(skill["name"])
        print(f"Deleted Skill '{skill['name']}' if it existed.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
