from __future__ import annotations

import sys
import unittest
from pathlib import Path

MODULE_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = MODULE_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

import safety_checks  # noqa: E402


class SafetyCheckTests(unittest.TestCase):
    def test_check_protected_class_language_positive(self) -> None:
        matches = safety_checks.check_protected_class_language(
            "Decline the claim because the driver is elderly and disabled."
        )
        self.assertIn("age", matches)
        self.assertIn("disability", matches)

    def test_check_protected_class_language_negative(self) -> None:
        matches = safety_checks.check_protected_class_language(
            "Request photos of the damaged bumper and a repair estimate."
        )
        self.assertEqual(matches, [])

    def test_check_fraud_signal_keywords_positive(self) -> None:
        matches = safety_checks.check_fraud_signal_keywords(
            "The claimant changed the story twice and supplied a synthetic invoice."
        )
        self.assertIn("story_shift", matches)
        self.assertIn("forged_documents", matches)

    def test_check_fraud_signal_keywords_negative(self) -> None:
        matches = safety_checks.check_fraud_signal_keywords(
            "A same-day photo set shows storm damage to the shed roof."
        )
        self.assertEqual(matches, [])

    def test_requires_citation_positive(self) -> None:
        self.assertTrue(safety_checks.requires_citation("The loss is excluded under the policy wording."))

    def test_requires_citation_negative_with_clause_reference(self) -> None:
        answer = "The loss is excluded under Clause HO-12 because wear and tear is not covered."
        self.assertFalse(safety_checks.requires_citation(answer))

    def test_requires_citation_negative_when_no_coverage_claim(self) -> None:
        answer = "Please provide the repair estimate and police report number."
        self.assertFalse(safety_checks.requires_citation(answer))


if __name__ == "__main__":
    unittest.main()
