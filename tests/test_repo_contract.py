"""Repo-wide contract tests runnable with `python -m unittest discover -s tests` from the repo root.

These supplement (not replace) each module's own tests/ directory and tests/run-all-validation.ps1.
Fully offline: no network, no Azure SDK calls.
"""
import json
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "shared" / "python"))

from secret_scan import scan_paths  # noqa: E402


class TestSharedTestData(unittest.TestCase):
    def test_policy_wordings_is_valid_json_list(self):
        path = REPO_ROOT / "shared" / "test-data" / "policy-wordings.json"
        self.assertTrue(path.exists(), f"{path} missing")
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        required_keys = {"id", "product", "policy_form", "section_ref", "clause_type", "title", "content"}
        for clause in data:
            self.assertTrue(required_keys.issubset(clause.keys()), f"Clause {clause.get('id')} missing keys")

    def test_no_real_subscription_or_tenant_ids_in_test_data(self):
        path = REPO_ROOT / "shared" / "test-data" / "policy-wordings.json"
        findings = scan_paths([path])
        self.assertEqual(findings, [], f"Unexpected findings in test data: {findings}")


class TestModuleConfigSchema(unittest.TestCase):
    def test_schema_file_is_valid_json(self):
        path = REPO_ROOT / "shared" / "schema" / "module-config.schema.json"
        schema = json.loads(path.read_text(encoding="utf-8"))
        self.assertIn("required", schema)
        self.assertIn("foundryEndpoint", schema["required"])

    def test_eval_case_schema_is_valid_json(self):
        path = REPO_ROOT / "shared" / "schema" / "eval-case.schema.json"
        schema = json.loads(path.read_text(encoding="utf-8"))
        self.assertIn("test_case_description", schema["properties"])


class TestRepoWideSecretScan(unittest.TestCase):
    def test_no_findings_in_root_docs(self):
        candidates = [
            REPO_ROOT / "README.md",
            REPO_ROOT / "SECURITY.md",
            REPO_ROOT / "CONTRIBUTING.md",
            REPO_ROOT / ".env.example",
        ]
        findings = scan_paths([p for p in candidates if p.exists()])
        self.assertEqual(findings, [], f"Unexpected findings: {findings}")


class TestModuleStructure(unittest.TestCase):
    """Verifies every modules/NN-* folder has the files CONTRIBUTING.md requires."""

    REQUIRED_FILES = [
        "README.md",
        "slides.md",
        "demo-runbook.md",
        "lab.md",
        "deploy.ps1",
        "verify.ps1",
        "cleanup.ps1",
        "config.example.json",
    ]

    def test_all_modules_have_required_files(self):
        modules_dir = REPO_ROOT / "modules"
        if not modules_dir.exists():
            self.skipTest("modules/ directory not present yet")
        module_dirs = sorted(p for p in modules_dir.iterdir() if p.is_dir())
        self.assertGreater(len(module_dirs), 0, "No module directories found")
        missing = {}
        for module_dir in module_dirs:
            missing_files = [f for f in self.REQUIRED_FILES if not (module_dir / f).exists()]
            if missing_files:
                missing[module_dir.name] = missing_files
        self.assertEqual(missing, {}, f"Modules missing required files: {missing}")


if __name__ == "__main__":
    unittest.main()
