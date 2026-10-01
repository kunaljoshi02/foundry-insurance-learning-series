from __future__ import annotations

import json
import unittest
from pathlib import Path


MODULE_ROOT = Path(__file__).resolve().parent.parent
CONFIG_EXAMPLE = MODULE_ROOT / "config.example.json"
SHARED_SCHEMA = MODULE_ROOT.parent.parent / "shared" / "schema" / "module-config.schema.json"


class ConfigExampleTests(unittest.TestCase):
    def test_config_example_is_valid_json(self) -> None:
        with CONFIG_EXAMPLE.open("r", encoding="utf-8") as handle:
            config = json.load(handle)

        self.assertIsInstance(config, dict)

    def test_required_shared_keys_exist(self) -> None:
        with CONFIG_EXAMPLE.open("r", encoding="utf-8") as handle:
            config = json.load(handle)
        with SHARED_SCHEMA.open("r", encoding="utf-8") as handle:
            schema = json.load(handle)

        for key in schema["required"]:
            self.assertIn(key, config, f"Missing shared required key: {key}")

    def test_module_specific_keys_exist(self) -> None:
        with CONFIG_EXAMPLE.open("r", encoding="utf-8") as handle:
            config = json.load(handle)

        for key in ("agentName", "agentDescription", "agentInstructionsFile", "tags"):
            self.assertIn(key, config, f"Missing module-specific key: {key}")

    def test_tags_match_course_convention(self) -> None:
        with CONFIG_EXAMPLE.open("r", encoding="utf-8") as handle:
            config = json.load(handle)

        tags = config.get("tags", {})
        self.assertEqual(tags.get("course"), "foundry-insurance-learning-series")
        self.assertEqual(tags.get("module"), "01-foundations-first-agent")

    def test_instruction_file_reference_exists(self) -> None:
        with CONFIG_EXAMPLE.open("r", encoding="utf-8") as handle:
            config = json.load(handle)

        instructions_file = MODULE_ROOT / config["agentInstructionsFile"]
        self.assertTrue(instructions_file.exists(), f"Missing instructions file: {instructions_file}")


if __name__ == "__main__":
    unittest.main()
