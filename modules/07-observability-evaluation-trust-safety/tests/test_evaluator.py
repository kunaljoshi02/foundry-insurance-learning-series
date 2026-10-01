from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

MODULE_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = MODULE_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

import evaluator  # noqa: E402


class EvaluatorTests(unittest.TestCase):
    def test_load_eval_dataset_reads_module_dataset(self) -> None:
        cases = evaluator.load_eval_dataset(MODULE_ROOT / "eval" / "triage-eval-dataset.json")
        self.assertGreaterEqual(len(cases), 10)
        self.assertTrue(all(case.get("test_case_description") for case in cases))

    def test_score_cases_calculates_pass_rate(self) -> None:
        cases = [
            {
                "id": "pass-case",
                "test_case_description": "routes correctly",
                "input": {"fnol_narrative": "simple glass claim"},
                "expected": {"route": "auto-adjudicate"},
            },
            {
                "id": "fail-case",
                "test_case_description": "routes incorrectly",
                "input": {"fnol_narrative": "injury claim"},
                "expected": {"route": "fraud-escalation"},
            },
        ]

        def stub_router(case: dict[str, object]) -> str:
            if case["id"] == "pass-case":
                return "auto-adjudicate"
            return "manual-review"

        scorecard = evaluator.score_cases(cases, router_fn=stub_router)
        self.assertEqual(scorecard["total"], 2)
        self.assertEqual(scorecard["passed"], 1)
        self.assertEqual(scorecard["failed"], 1)
        self.assertAlmostEqual(scorecard["pass_rate"], 0.5)

    def test_default_router_detects_fraud_and_manual_review(self) -> None:
        fraud_case = {
            "input": {"fnol_narrative": "The claimant submitted altered receipts and a synthetic invoice."}
        }
        manual_case = {
            "input": {"fnol_narrative": "A third party alleges injury and there is a liability dispute."}
        }
        auto_case = {
            "input": {"fnol_narrative": "A documented burst pipe damaged the kitchen floor."}
        }

        self.assertEqual(evaluator.default_router(fraud_case)["route"], "fraud-escalation")
        self.assertEqual(evaluator.default_router(manual_case)["route"], "manual-review")
        self.assertEqual(evaluator.default_router(auto_case)["route"], "auto-adjudicate")

    def test_write_scorecard_persists_json(self) -> None:
        output_path = MODULE_ROOT / "artifacts" / "unit-test-scorecard.json"
        output_path.parent.mkdir(exist_ok=True)
        payload = {"total": 1, "passed": 1, "failed": 0, "pass_rate": 1.0, "per_case": []}
        evaluator.write_scorecard(payload, output_path)
        reloaded = json.loads(output_path.read_text(encoding="utf-8"))
        self.assertEqual(reloaded["pass_rate"], 1.0)
        output_path.unlink()
        if not any(output_path.parent.iterdir()):
            output_path.parent.rmdir()


if __name__ == "__main__":
    unittest.main()
