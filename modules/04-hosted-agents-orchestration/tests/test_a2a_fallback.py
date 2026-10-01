import os
import sys
import unittest


TESTS_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.abspath(os.path.join(TESTS_DIR, "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from adjudicator_stub.respond import respond  # noqa: E402
from triage_agent.a2a_client import (  # noqa: E402
    A2AProtocolError,
    call_adjudicator_via_a2a,
    invoke_with_fallback,
    is_hosted_agent_not_supported,
)


class A2AFallbackTests(unittest.TestCase):
    def setUp(self):
        self.a2a_url = (
            "https://<foundry-endpoint>/api/projects/<project>/agents/"
            "coverage-settlement-adjudicator/endpoint/protocols/a2a?api-version=v1"
        )
        self.fnol = {
            "policy_number": "HOME-1001",
            "fnol_narrative": (
                "A sudden washing machine hose failure caused water damage in the kitchen."
            ),
        }

    def test_success_envelope_does_not_trigger_fallback(self):
        calls = {"fallback": 0}
        a2a_result = {
            "decision": "COVERED",
            "rationale": "Sudden escape of water is covered.",
            "indicative_settlement": "$7,800",
        }

        def transport(url, payload, headers):
            self.assertEqual(url, self.a2a_url)
            self.assertEqual(payload["method"], "message/send")
            return {"jsonrpc": "2.0", "id": payload["id"], "result": a2a_result}

        def fallback_callable(_responses_url, _fnol):
            calls["fallback"] += 1
            return {"decision": "SHOULD NOT RUN"}

        outcome = invoke_with_fallback(
            self.a2a_url,
            self.fnol,
            transport=transport,
            fallback_callable=fallback_callable,
        )

        self.assertFalse(outcome.used_fallback)
        self.assertEqual(outcome.protocol, "a2a")
        self.assertEqual(outcome.result, a2a_result)
        self.assertEqual(calls["fallback"], 0)

    def test_hosted_agent_not_supported_triggers_fallback(self):
        def transport(_url, payload, _headers):
            return {
                "jsonrpc": "2.0",
                "id": payload["id"],
                "error": {
                    "code": -32099,
                    "data": {
                        "code": "HostedAgentNotSupported",
                        "detail": "Use a prompt agent as the A2A target.",
                    },
                },
            }

        def fallback_callable(responses_url, fnol):
            self.assertIn("/endpoint/protocols/openai/responses", responses_url)
            return respond(fnol)

        outcome = invoke_with_fallback(
            self.a2a_url,
            self.fnol,
            transport=transport,
            fallback_callable=fallback_callable,
        )

        self.assertTrue(outcome.used_fallback)
        self.assertEqual(outcome.protocol, "responses")
        self.assertEqual(outcome.result["decision"], "COVERED")

    def test_detection_helper_returns_expected_booleans(self):
        success_payload = {"jsonrpc": "2.0", "id": "1", "result": {"status": "ok"}}
        hosted_error_payload = {
            "jsonrpc": "2.0",
            "id": "2",
            "error": {
                "code": -32099,
                "data": {
                    "code": "HostedAgentNotSupported",
                    "detail": "Use a prompt agent as the A2A target.",
                },
            },
        }
        unrelated_error_payload = {
            "jsonrpc": "2.0",
            "id": "3",
            "error": {
                "code": -32001,
                "data": {"code": "Unauthorized", "detail": "Caller lacks permission."},
            },
        }

        self.assertFalse(is_hosted_agent_not_supported(success_payload))
        self.assertTrue(is_hosted_agent_not_supported(hosted_error_payload))
        self.assertFalse(is_hosted_agent_not_supported(unrelated_error_payload))

    def test_unrelated_json_rpc_error_propagates(self):
        def transport(_url, payload, _headers):
            return {
                "jsonrpc": "2.0",
                "id": payload["id"],
                "error": {
                    "code": -32001,
                    "data": {"code": "Unauthorized", "detail": "Caller lacks permission."},
                },
            }

        with self.assertRaises(A2AProtocolError):
            call_adjudicator_via_a2a(self.a2a_url, self.fnol, transport=transport)


if __name__ == "__main__":
    unittest.main()

