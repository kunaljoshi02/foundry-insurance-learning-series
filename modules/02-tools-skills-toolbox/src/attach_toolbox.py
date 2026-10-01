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
    parser = argparse.ArgumentParser(description="Attach the module toolbox to the target agent.")
    parser.add_argument("--config", required=True, help="Path to config.json")
    parser.add_argument("--what-if", action="store_true", help="Show planned actions only")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        config = load_config(
            args.config,
            required_keys=["foundryEndpoint", "agentName", "toolboxName"],
        )
    except ConfigError as exc:
        print(exc)
        return 1

    if args.what_if:
        print(f"[WhatIf] Would attach toolbox '{config['toolboxName']}' to agent '{config['agentName']}'.")
        return 0

    client = FoundryToolboxClient(config["foundryEndpoint"])
    current = client.get_agent_toolboxes(config["agentName"])
    current_names = sorted({item.get("name") for item in current if item.get("name")})

    if config["toolboxName"] in current_names:
        print(f"Agent '{config['agentName']}' already references toolbox '{config['toolboxName']}'.")
        return 0

    desired = sorted(set(current_names + [config["toolboxName"]]))
    client.set_agent_toolboxes(config["agentName"], desired)
    print(f"Attached toolbox '{config['toolboxName']}' to agent '{config['agentName']}'.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
