from __future__ import annotations

import sys
import unittest
from pathlib import Path


MODULE_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = MODULE_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from auth_context import AuthContext, predict_obo_outcome  # type: ignore  # noqa: E402


class AuthContextTests(unittest.TestCase):
    def assert_reason(self, reason: str, *keywords: str) -> None:
        self.assertTrue(reason.strip(), "Reason should not be empty.")
        lowered = reason.lower()
        for keyword in keywords:
            self.assertIn(keyword.lower(), lowered)

    def test_interactive_user_succeeds(self) -> None:
        will_succeed, reason = predict_obo_outcome(
            AuthContext(is_interactive=True, has_user_token=True, principal_type="User")
        )
        self.assertTrue(will_succeed)
        self.assert_reason(reason, "interactive", "user token")

    def test_service_principal_fails(self) -> None:
        will_succeed, reason = predict_obo_outcome(
            AuthContext(is_interactive=False, has_user_token=False, principal_type="ServicePrincipal")
        )
        self.assertFalse(will_succeed)
        self.assert_reason(reason, "service-principal", "user principal")

    def test_non_interactive_user_fails(self) -> None:
        will_succeed, reason = predict_obo_outcome(
            AuthContext(is_interactive=False, has_user_token=True, principal_type="User")
        )
        self.assertFalse(will_succeed)
        self.assert_reason(reason, "interactive", "background")

    def test_missing_user_token_fails(self) -> None:
        will_succeed, reason = predict_obo_outcome(
            AuthContext(is_interactive=True, has_user_token=False, principal_type="User")
        )
        self.assertFalse(will_succeed)
        self.assert_reason(reason, "delegated", "user token")


if __name__ == "__main__":
    unittest.main()
