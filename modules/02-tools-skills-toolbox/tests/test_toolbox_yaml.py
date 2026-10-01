from __future__ import annotations

import re
import unittest
from pathlib import Path


MODULE_ROOT = Path(__file__).resolve().parents[1]
TOOLBOX_PATH = MODULE_ROOT / "src" / "toolbox.yaml"
SKILLS_ROOT = MODULE_ROOT / "src" / "skills"
EXPECTED_SKILLS = {
    "adjudication-rationale",
    "claims-tone",
    "customer-comms-tone",
    "regulatory-disclosure",
    "underwriting-appetite",
}


def parse_toolbox_yaml(path: Path) -> dict:
    try:
        import yaml  # type: ignore
    except ImportError:
        return parse_minimal_yaml(path)

    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def parse_minimal_yaml(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    result: dict[str, object] = {"skills": [], "tools": []}
    current_section: str | None = None
    current_tool: dict[str, object] | None = None

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if not raw_line.startswith(" "):
            current_tool = None
            if stripped.startswith("description:"):
                result["description"] = stripped.split(":", 1)[1].strip()
            elif stripped == "skills:":
                current_section = "skills"
            elif stripped == "tools:":
                current_section = "tools"
            continue

        if current_section == "skills":
            match = re.match(r"\s*-\s+name:\s*(.+)$", raw_line)
            if match:
                casted = result["skills"]
                assert isinstance(casted, list)
                casted.append({"name": match.group(1).strip()})
        elif current_section == "tools":
            type_match = re.match(r"\s*-\s+type:\s*(.+)$", raw_line)
            if type_match:
                current_tool = {"type": type_match.group(1).strip()}
                casted = result["tools"]
                assert isinstance(casted, list)
                casted.append(current_tool)
                continue

            if current_tool is not None:
                name_match = re.match(r"\s+name:\s*(.+)$", raw_line)
                if name_match:
                    current_tool["name"] = name_match.group(1).strip()

    return result


class ToolboxYamlTests(unittest.TestCase):
    def test_toolbox_yaml_exists(self) -> None:
        self.assertTrue(TOOLBOX_PATH.exists(), "src/toolbox.yaml should exist")

    def test_toolbox_yaml_parses(self) -> None:
        data = parse_toolbox_yaml(TOOLBOX_PATH)
        self.assertIsInstance(data, dict)
        self.assertIn("skills", data)
        self.assertIn("tools", data)

    def test_toolbox_references_expected_skills(self) -> None:
        data = parse_toolbox_yaml(TOOLBOX_PATH)
        skills = data.get("skills", [])
        skill_names = {item["name"] for item in skills}
        self.assertEqual(skill_names, EXPECTED_SKILLS)

    def test_skill_files_exist_for_referenced_skills(self) -> None:
        for skill_name in EXPECTED_SKILLS:
            skill_path = SKILLS_ROOT / skill_name / "SKILL.md"
            self.assertTrue(skill_path.exists(), f"Missing Skill file: {skill_path}")

    def test_only_one_tool_is_defined_and_it_is_code_interpreter(self) -> None:
        data = parse_toolbox_yaml(TOOLBOX_PATH)
        tools = data.get("tools", [])
        self.assertEqual(len(tools), 1)
        self.assertEqual(tools[0]["type"], "code_interpreter")


if __name__ == "__main__":
    unittest.main()
