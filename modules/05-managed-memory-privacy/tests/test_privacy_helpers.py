from __future__ import annotations

import sys
import unittest
from pathlib import Path


MODULE_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = MODULE_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from privacy_tools import redact_for_log  # type: ignore  # noqa: E402


class RedactForLogTests(unittest.TestCase):
    def test_empty_string_returns_placeholder(self) -> None:
        self.assertEqual(redact_for_log(""), "<empty>")
        self.assertEqual(redact_for_log("   "), "<empty>")

    def test_long_text_is_truncated(self) -> None:
        text = "Remember that I prefer settlement summaries in bullet points with the likely outcome first and no more than five bullets."
        redacted = redact_for_log(text)
        self.assertTrue(redacted.endswith("..."))
        self.assertLessEqual(len(redacted), 48)

    def test_email_addresses_are_redacted(self) -> None:
        redacted = redact_for_log("Remember my contact alias is trainer@example.com")
        self.assertNotIn("trainer@example.com", redacted)
        self.assertIn("[redacted-email]", redacted)

    def test_digits_are_masked(self) -> None:
        redacted = redact_for_log("Use claim example 12345 in slide 2.")
        self.assertNotIn("12345", redacted)
        self.assertIn("XXXXX", redacted)


if __name__ == "__main__":
    unittest.main()
