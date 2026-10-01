from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


MODULE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = MODULE_ROOT.parents[1]
BUILD_SCRIPT = MODULE_ROOT / "src" / "build_search_index.py"
DATASET_PATH = REPO_ROOT / "shared" / "test-data" / "policy-wordings.json"


spec = importlib.util.spec_from_file_location("build_search_index", BUILD_SCRIPT)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class IndexSchemaTests(unittest.TestCase):
    def test_dataset_exists(self) -> None:
        self.assertTrue(DATASET_PATH.exists(), "shared/test-data/policy-wordings.json should exist")

    def test_declared_schema_covers_dataset_keys(self) -> None:
        records = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
        self.assertIsInstance(records, list)
        self.assertGreater(len(records), 0)

        dataset_keys = set().union(*(record.keys() for record in records))
        declared = set(module.SCHEMA_FIELD_NAMES)
        self.assertTrue(
            dataset_keys.issubset(declared),
            f"Dataset keys {sorted(dataset_keys)} must be a subset of declared schema fields {sorted(declared)}",
        )

    def test_expected_grounding_fields_are_present(self) -> None:
        declared = set(module.SCHEMA_FIELD_NAMES)
        self.assertIn("content", declared)
        self.assertIn("section_ref", declared)
        self.assertIn("content_vector", declared)


if __name__ == "__main__":
    unittest.main()
