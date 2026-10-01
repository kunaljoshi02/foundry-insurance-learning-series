from __future__ import annotations

import json
import socket
import sys
import threading
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path

MODULE_ROOT = Path(__file__).resolve().parent.parent
SRC_ROOT = MODULE_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from mock_deployment_probe_server import (  # noqa: E402
    build_deployment_metadata_response,
    create_server,
)


def get_free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


class DeploymentProbeContractTests(unittest.TestCase):
    def test_build_response_returns_arm_shaped_resource(self) -> None:
        model_name = "gpt-4.1-mini"
        payload = build_deployment_metadata_response(model_name)

        self.assertEqual(payload["name"], model_name)
        self.assertTrue(payload["id"].endswith(f"/deployments/{model_name}"))
        self.assertEqual(payload["type"], "Microsoft.CognitiveServices/accounts/deployments")
        self.assertEqual(payload["sku"]["name"], "GlobalStandard")
        self.assertEqual(payload["properties"]["provisioningState"], "Succeeded")
        self.assertEqual(payload["properties"]["model"]["name"], model_name)
        self.assertEqual(payload["properties"]["model"]["format"], "OpenAI")
        self.assertEqual(payload["properties"]["model"]["version"], "2025-01-01")

    def test_second_model_name_is_supported(self) -> None:
        model_name = "billing-claims-mini"
        payload = build_deployment_metadata_response(model_name)

        self.assertEqual(payload["name"], model_name)
        self.assertTrue(payload["id"].endswith(f"/deployments/{model_name}"))
        self.assertEqual(payload["properties"]["model"]["name"], model_name)

    def test_http_server_returns_expected_payload_without_api_version(self) -> None:
        model_name = "claims-gateway"
        port = get_free_port()
        server = create_server("127.0.0.1", port, model_name)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        time.sleep(0.1)

        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/deployments/{model_name}") as response:
                self.assertEqual(response.status, 200)
                payload = json.loads(response.read().decode("utf-8"))

            self.assertEqual(payload["name"], model_name)
            self.assertEqual(payload["type"], "Microsoft.CognitiveServices/accounts/deployments")
            self.assertEqual(payload["properties"]["model"]["name"], model_name)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

    def test_http_server_rejects_api_version_for_probe(self) -> None:
        model_name = "claims-gateway"
        port = get_free_port()
        server = create_server("127.0.0.1", port, model_name)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        time.sleep(0.1)

        try:
            with self.assertRaises(urllib.error.HTTPError) as raised:
                with urllib.request.urlopen(
                    f"http://127.0.0.1:{port}/deployments/{model_name}?api-version=2025-01-01"
                ):
                    pass

            self.assertEqual(raised.exception.code, 400)
            raised.exception.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
