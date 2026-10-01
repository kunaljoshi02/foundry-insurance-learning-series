from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

MODULE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = MODULE_ROOT.parents[1]
sys.path.insert(0, str(REPO_ROOT / "shared" / "python"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config_loader import ConfigError, load_config  # type: ignore  # noqa: E402
from foundry_toolbox_client import FoundryApiError, FoundryToolboxClient  # type: ignore  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect Skills, toolbox, and agent attachment.")
    parser.add_argument("--config", required=True, help="Path to config.json")
    parser.add_argument("--check-agent", action="store_true", help="Also confirm agent toolbox attachment")
    return parser.parse_args()


def pretty(data: object) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)


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

    client = FoundryToolboxClient(config["foundryEndpoint"])

    print("Skills")
    print("------")
    for skill in config["skills"]:
        payload = client.get_skill(skill["name"])
        if payload is None:
            print(f"- {skill['name']}: NOT FOUND")
            return 1
        print(f"- {skill['name']}:")
        print(pretty(payload))

    print("\nToolbox")
    print("-------")
    toolbox = client.get_toolbox(config["toolboxName"])
    if toolbox is None:
        print(f"Toolbox '{config['toolboxName']}' was not found.")
        return 1
    print(pretty(toolbox))

    if args.check_agent:
        print("\nAgent attachment")
        print("----------------")
        try:
            toolboxes = client.get_agent_toolboxes(config["agentName"])
        except FoundryApiError as exc:
            print(exc)
            return 1

        print(pretty(toolboxes))
        if config["toolboxName"] not in {item.get("name") for item in toolboxes}:
            print(f"Agent '{config['agentName']}' does not reference toolbox '{config['toolboxName']}'.")
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
